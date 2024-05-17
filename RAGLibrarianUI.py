import sys
import json
from os import listdir, path, makedirs
from datetime import datetime

from PySide6.QtCore import Qt, QSettings

from PySide6.QtWidgets import (
	QApplication, QMainWindow, QSplitter, QVBoxLayout, QHBoxLayout,
	QLabel, QTextEdit, QComboBox, QSlider, QLineEdit, QPushButton, QWidget, QSpacerItem,
	QSizePolicy,QFileDialog,QTextBrowser,
)


CSS_TEMPLATE= """
<style>
		.bubble {
			position: relative;
			padding: 10px;
			border-radius: 40px; /* rounded corners */
			display: inline-block;
			margin: 10px;
		}
		.bubble::before {
			content: "";
			position: absolute;
			top: 50%;
			transform: translateY(-50%);
			border-top: 10px solid transparent;
			border-bottom: 10px solid transparent;
		}
		.bubble.left {
			background-color: #f0f0f0;
			left: 20%; /* 10% offset to the right */
		}
		.bubble.left::before {
			left: -60px;
			border-right: 20px solid #f0f0f0;
		}
		.bubble.right {
			background-color: #cff;
			right: 20%; /* 10% offset to the left */
		}
		.bubble.right::before {
			right: -20px;
			border-left: 20px solid #cff;
		}
	</style>"""

DIALOGUE_TEMPLATE= """
	<div class="bubble left"> User: {question} <br></div>
	<div class="bubble right"> AI: {answer} <br></div>"""


class ChatHistory:
	def __init__(self, css, chat_item_template):
			self._css = css
			self._chat_item_template = chat_item_template
				
			self.reset()

	def chat_item(self, question, answer, timestamp=None):
		if timestamp is None:
			timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		return {'question': question, 'answer': answer, 'timestamp' : timestamp}
	
	def chat_item_to_html(self, question, answer):
		return self._chat_item_template.format(question=question, answer=answer)
	
	def append(self, question, answer, timestamp=None):	
		item = self.chat_item(question, answer, timestamp)
		self._history.append(item)
		self._history_html += self.chat_item_to_html(question=question, answer=answer)

	def get(self, html=True):
		if html:
			return(self._history_html)
		else:
			return(self._history)
		
	def reset(self):
		self._history = []
		#self._history_html=""
		self._history_html = self._css



class MainWindow(QMainWindow):
	def __init__(self, librarian, llm_path="./models", chathistory_path = "./chathistory/"):
		super().__init__()

		self.librarian = librarian

		self._historypath = chathistory_path
		if not path.exists(self._historypath):
			makedirs(self._historypath)

		self._llm_path = llm_path
		if not path.exists(self._llm_path):
			makedirs(self._llm_path)

		self.chat_history=ChatHistory(css=CSS_TEMPLATE, chat_item_template=DIALOGUE_TEMPLATE)

		self.setWindowTitle("RAG Librarian")
		self.setMinimumSize(800, 600)

		# Load window settings
		settings = QSettings("AIinMedicine", "RAGLibrarian")
		self.restoreGeometry(settings.value("geometry"))

		# Create main layout
		central_widget = QWidget()
		main_layout = QHBoxLayout()
		central_widget.setLayout(main_layout)
		self.setCentralWidget(central_widget)

		# Create main splitter
		self.main_splitter = QSplitter(Qt.Horizontal)
		main_layout.addWidget(self.main_splitter)
		self.main_splitter.restoreState(settings.value("splitterState"))

		# Create parameters section
		parameters_section = QWidget()
		parameters_layout = QVBoxLayout()
		parameters_section.setLayout(parameters_layout)
		self.main_splitter.addWidget(parameters_section)

		# Add parameters section widgets
		self.llm_selector = QComboBox()
		llms = listdir("./models")
		print("LLMs found:" + str(llms))
		self.llm_selector.addItems(llms)
		self.llm_selector.currentIndexChanged.connect(self.select_llm)
		parameters_layout.addWidget(self.llm_selector)

		temperature_slider = QSlider(Qt.Horizontal)
		temperature_slider.setRange(0, 100)
		temperature_slider.setValue(50)
		temperature_slider.valueChanged.connect(self.set_llm_parameters)
		parameters_layout.addWidget(temperature_slider)

		llm_parameters_line = QLineEdit()
		parameters_layout.addWidget(llm_parameters_line)

		# Add spacer to make parameters section expandable
		spacer_item = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
		parameters_layout.addItem(spacer_item)

		# Create display section
		display_section = QWidget()
		display_layout = QVBoxLayout()
		display_section.setLayout(display_layout)
		self.main_splitter.addWidget(display_section)

		title_label = QLabel("<b>Yor questions answered</b>")
		display_layout.addWidget(title_label)

		self.chat_display = QTextBrowser()
		#self.chat_display.setReadOnly(True)
		display_layout.addWidget(self.chat_display, 3)
		self.chat_display.setStyleSheet(CSS_TEMPLATE)
		#self.chat_display.setHtml(CSS_TEMPLATE)

		input_splitter = QSplitter(Qt.Vertical)
		display_layout.addWidget(input_splitter)

		self.user_input = QTextEdit()
		
		user_input_label = QLabel("<b>Your question:</b>")
		input_layout = QVBoxLayout()
		input_layout.addWidget(user_input_label)
		input_layout.addWidget(self.user_input)
		input_widget = QWidget()
		input_widget.setLayout(input_layout)
		input_splitter.addWidget(input_widget)

		actions_layout = QHBoxLayout()
		display_layout.addLayout(actions_layout)

		run_query_button = QPushButton("Run query")
		run_query_button.setDefault(True)
		run_query_button.clicked.connect(self.run_query)
		actions_layout.addWidget(run_query_button)

		upload_context_button = QPushButton("Upload context")
		upload_context_button.clicked.connect(self.upload_context)
		actions_layout.addWidget(upload_context_button)

		new_chat_button = QPushButton("New chat")
		new_chat_button.clicked.connect(self.new_chat)
		actions_layout.addWidget(new_chat_button)

		# Add menu bar
		menu_bar = self.menuBar()
		file_menu = menu_bar.addMenu("File")
		file_menu.addAction("Open", self.open_file)
		file_menu.addAction("Save", self.save_file)
		file_menu.addAction("Clear", self.clear_chat)
		file_menu.addAction("Settings", self.show_settings)

	def closeEvent(self, event):
		# Save window settings
		settings = QSettings("MyCompany", "MyApp")
		settings.setValue("geometry", self.saveGeometry())
		settings.setValue("splitterState", self.main_splitter.saveState())
		super().closeEvent(event)

	# Implement your associated functions here
	def select_llm(self, index):
		print("Selected LLM:" + self.llm_selector.currentText())

	def set_llm_parameters(self, value):
		pass

	def run_query(self):
		question = self.user_input.toPlainText()
		answer=self.librarian.run_query(question)
		self.chat_history.append(question=question, answer=answer)
		self.show_chat()

	def show_chat(self):
		text = self.chat_history.get(html=True)
		self.chat_display.setHtml(text)
		self.user_input.setText("")
		
	def process_file(self, file_name):
		self.librarian.ingest_documents(file_name, is_single_file=True)
		

	def upload_context(self):
		file_dialog = QFileDialog()
		file_dialog.setFileMode(QFileDialog.AnyFile)
		file_dialog.setNameFilter("Text files (*.pdf)")
		if file_dialog.exec():
			file_name = file_dialog.selectedFiles()[0]
			self.process_file(file_name)


	def new_chat(self):
		self.chat_history.reset()
		self.chat_display.setText("")
		self.user_input.setText("")

	def open_file(self):
		file_dialog = QFileDialog()
		file_dialog.setFileMode(QFileDialog.AnyFile)
		file_dialog.setNameFilter("Text files (*.json)")
		if file_dialog.exec():
			file_name = file_dialog.selectedFiles()[0]
			with open(file_name) as f:	
				data = json.load(f)
			self.chat_history.reset()
			for item in data:
				self.chat_history.append(question=item['question'], answer=item['answer'])
			self.show_chat()
				

	def save_file(self):
		timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
		with open(self._historypath + f'chathistory_{timestamp}.json', 'w') as f:
			json.dump(self.chat_history.get(html=False), f)

	def clear_chat(self):
		self.new_chat()

	def show_settings(self):
		pass

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec())