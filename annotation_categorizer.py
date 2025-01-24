import os
import argparse

def read_terms(filename : str = 'annotation_categories.txt') -> dict:
    """Reads the annotation configuration file with annotation terms and their categories 
    and returns a dictionary with {term:category}.
    
    Args:   
        filename (str): the name of the file to read from
        This file has to be in the format of term:category, one per line."""
    terms = {}
    with open(filename, 'r') as f:
        lines = f.readlines()
        for line in lines:
            term, category = line.strip().split(':')
            terms[term] = category
    return(terms)

def categorize_annotations(annotation_file : str, terms : dict) -> str:
    """Reads an annotation file and categorizes the annotations according to the terms dictionary.

    Args:
        annotation_file (str): the name of the annotation file to read from
        terms (dict): a dictionary with {term:category} to categorize the annotations
    Returns:
        str: a string with the categorized annotations"""
    with open(annotation_file, 'r') as f:
        categorized=""
        lines = f.readlines()
        for line in lines:
            words = line.strip().split(' ') #the first word in the line
            term= words[1]
            category = terms.get(term, '') #if not found, return empty string
            if category:
                words[1] = category
            categorized += ' '.join(words) + '\n'
    return(categorized)

if __name__ == '__main__':
    #parse arguments
    parser = argparse.ArgumentParser(description='Categorize annotations')
    parser.add_argument('-i', '--input_dir', type=str, required=True, help='The directory with the annotation files')

    input_dir=parser.parse_args().input_dir
    #read our terms translation file
    terms = read_terms()
    #for each annotation file in the annotations directory
    for filename in os.listdir(input_dir):
        if filename.endswith('.ann'):
            fname = os.path.join(input_dir, filename)
            categorized = categorize_annotations(fname, terms)
            #write the categorized annotations to a new file with the extension .anx'
            outfilename = os.path.join(input_dir, filename.replace('.ann', '.anx'))
            with open(outfilename, 'w') as f:
                f.write(categorized)
    
