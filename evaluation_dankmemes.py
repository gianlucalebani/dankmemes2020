#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import glob
import getopt
import itertools

import numpy as np
import pandas as pd

from sklearn.metrics import precision_recall_fscore_support, silhouette_score


def help_msg():
    print("""\
This evaluation script can be used to parse all the Dank Memes 2020 result 
files inside a folder and to evaluate them against the appropriate gold 
standard. The scores are written in a single output file specified by the user.

IMPORTANT: The rsubmitted results files are also checked for consistency 
against the format speciffied in the guidelines. All files not conforming to 
this format are ignored.\
""")


def usage():
    print("""
General Usage:
> python evaluation_dankmemes.py [-h] [-r path_to_results_folder] 
[-g path_to_gold_standard_folder] [-o path_to_output_file]

    [-h|--help]    >> print this help
    [-r|--results] >> path/to/results/files/folder
    [-g|--gold]    >> path/to/gold/standard/files/folder
    [-o|--output]  >> path/to/output/file (default is "./evaluation.txt") 
""")


def extract_metadata(resfile):
    """
    Reads a filename formatted according to the guidelines and returns
    the metadata of the run

    Parameters
    ----------
    filename : str
        name of the files encoding the run infos

    Returns
    -------
    metadata : dict
        metadata of the run
        keys of the dictionary: task_name, team_name, run_id
    """
    metadata = dict()
    tasks = set(["task1", "task2", "task3_labelled", "task3_unlabelled",
                 "task3_unlabelled_distances"])
    
    filename = os.path.basename(resfile)
    spl_name = os.path.splitext(filename)[0].split("-")

    try:
        metadata["task_name"] = spl_name[1]
		# in case someone used the hyphen in the team name
        metadata["team_name"] = "-".join(spl_name[2:-1])  
        metadata["run_id"] = spl_name[-1]
    except IndexError:
        return None
    
    # let's check if the name is properly formatted (let's ignore the run_id)       
    if spl_name[0] != "dankmemes" or\
        metadata["task_name"] not in tasks:
        return None
    
    return metadata

    
def sanity_check(results_folder):
    """
    This function checks if the csv files in the results folder adhere to the 
    format specified in the task guidelines. Issues a warning for each 
    ill-formatted file
    
    Parameters
    ----------
    results_folder : path
        Path to results folder

    Returns
    -------
    the list of properly formatted files
    """
    filtered_results = []
    for resfile in glob.glob(os.path.join(results_folder, "*.csv")):
        
        # let's check if the filename is properly formatted
        metadata = extract_metadata(resfile)
        
        if metadata is None:
            print(f'Warning: the filename "{resfile}" doesn\'t follow the '\
                  "format described in the guidelines and will be ignored.")
            continue
        
        # let's check if the csv file is properly formatted
        res_df = pd.read_csv(resfile, header = 0)
        
        if metadata["task_name"] == "task3_unlabelled_distances":
            if res_df.columns.to_list() != ["Image 1", "Image 2", "Distance"]:
                print(f'Warning: the file "{resfile}" isn\'t properly '\
                      "formatted and will be ignored.")     
                continue
        elif res_df.columns.to_list() != ["File", "Label"]:
            print(f'Warning: the file "{resfile}" isn\'t properly '\
                  "formatted and will be ignored.")     
            continue

        filtered_results.append(resfile)

    return filtered_results


def evaluation(results, gold, output_file):
    """
    This is the main evaluation function: it reads the properly formatted
    results files, compare them against the gold standard (if relevant)
    and write out the results in the output_file

    Parameters
    ----------
    results : list
        List of properly formatted results files.
    golds : path
        Path to the folder containig the gold standard files.
    output_file : file
        Path to the file on which the evalation scores will be written.

    Returns
    -------
    None
    """    
    # let's parse the gold standards files
    gold_standards = dict()
    for goldfile in glob.glob(os.path.join(gold, "*.csv")):
        
        if os.path.basename(goldfile).startswith("meme"):
            df =  pd.read_csv(
                goldfile, header = 0, usecols=["File", "Meme"])
            df.rename(columns = {"Meme": "Gold"}, inplace = True)
            gold_standards["task1"] = df
        elif os.path.basename(goldfile).startswith("hate"):
            df =  pd.read_csv(
                goldfile, header = 0, usecols=["File", "Hate Speech"])
            df.rename(columns = {"Hate Speech": "Gold"}, inplace = True)
            gold_standards["task2"] = df            
        elif os.path.basename(goldfile).startswith("event"):
            df =  pd.read_csv(
                goldfile, header = 0, usecols=["File", "Event"])
            df.rename(columns = {"Event": "Gold"}, inplace = True)
            gold_standards["task3"] = df  
        else:
            raise ValueError(f'"{goldfile}" is not a valid filename for a '\
                             'gold standard file. Please fix this.')
    
    # let's parse the results files, evaluate them and export the evaluation results
    with open(output_file, "w") as outfile:
        for result_file in results:
            metadata = extract_metadata(result_file)
            
            heading = "\n".join([
                    f'TEAM: {metadata["team_name"]}',
                    f'TASK: {metadata["task_name"]}',
                    f'RUN: {metadata["run_id"]}\n\n'])

            # the distances file has a different structure,
            if not "distances" in metadata["task_name"]:  
                resdf = pd.read_csv(result_file, header = 0)
                gs = gold_standards[metadata["task_name"].split("_")[0]]
                
                joined_df = resdf.set_index('File').join(gs.set_index('File'))
                
                outfile.write(heading)
                
                outfile.write("Sanity Check:\n")
                outfile.write('- number of missing Labels:'\
                              f'{joined_df["Label"].isna().sum()}\n')
                outfile.write('- number of Labels NOT belonging to the test set:'\
                              f'{joined_df["Gold"].isna().sum()}\n\n')
                
                # task 1 and 2 are binary
                if metadata["task_name"] in ["task1", "task2"]:  
                    prec, rec, f1, _  = precision_recall_fscore_support(
                            joined_df[['Gold']].to_numpy(),
                            joined_df[['Label']].to_numpy(), 
                            average = "binary")
                    
                    outfile.write("\n".join([
                            'Model Evaluation:',
                            f'- PRECISION: {round(prec, 4)}',
                            f'- RECALL: {round(rec, 4)}',
                            f'- F1 SCORE: {round(f1, 4)}\n\n']))
    
                # we use macro average in the supervised versions of the third task
                elif "_labelled" in metadata["task_name"]:  
                    prec, rec, f1, _  = precision_recall_fscore_support(
                            joined_df[['Gold']].to_numpy(),
                            joined_df[['Label']].to_numpy(), 
                            average = "macro")
                    
                    outfile.write("\n".join([
                            'Model Evaluation:',
                            f'- MACRO-AVERAGED PRECISION: {round(prec, 4)}',
                            f'- MACRO-AVERAGED RECALL: {round(rec, 4)}',
                            f'- MACRO-AVERAGED F1 SCORE: {round(f1, 4)}\n\n']))
    
                # when dealing with clustering, P, R & F1 are calculated 
                # following Manning et al (2008) 
                # see https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-clustering-1.html
                else:
                    cols = ["Files", "Label", "Gold"]
                    pairwise_comparisons = []
                    for pair in itertools.permutations(joined_df.index, 2):
                        row = [pair]
                        pairwise_comparisons.append(row)

                        for col in cols[1:]:
                            if joined_df[col][pair[0]] == joined_df[col][pair[1]]:
                                row.append(1)
                            else:
                                row.append(0)                       
                    
                    pairs_df = pd.DataFrame(
                            pairwise_comparisons, columns = cols)
                    
                    prec, rec, f1, _  = precision_recall_fscore_support(
                            pairs_df[['Gold']].to_numpy(),
                            pairs_df[['Label']].to_numpy(), 
                            average = "binary")
                    
                    outfile.write("\n".join([
                            'Model Evaluation:',
                            f'- PRECISION: {round(prec, 4)}',
                            f'- RECALL: {round(rec, 4)}',
                            f'- F1 SCORE: {round(f1, 4)}\n\n']))
                
            # we use the distances file to calculate the silhouette score    
            else:
                
                # look for the labels file in the same folder 
                labels_file = result_file.replace(
                        "_unlabelled_distances", "_unlabelled")
                
                try:
                    labels_df = pd.read_csv(labels_file, header = 0)
                    cluster_labels = labels_df["Label"].to_numpy()                    
                    file2id = dict((v,k) for k,v in labels_df["File"].to_dict().items())
                except FileNotFoundError:
                    print(f'Warning: unable to find "{labels_file}", so that'\
                          f"{result_file} will be ignored.")
                    continue
                
                outfile.write(heading) 
                
                # let's rearrange the distances in result_file in a square matrix
                sample_size = len(labels_df.index)
                distances = np.empty([sample_size, sample_size])
                distances[:] = np.NaN
                
                resdf = pd.read_csv(result_file, header = 0)
                for _, (file1, file2, dist) in resdf.iterrows():
                    id_file1 = file2id[file1]
                    if_file2 = file2id[file2]
                    distances[id_file1, if_file2] = dist
                    distances[if_file2, id_file1] = dist

                # let's check if there are nans in our matrix
                if np.isnan(distances).sum() > 0:
                    warning = "Warning: it looks some pairwise distances are "\
                    f"missing from '{result_file}'. This may affect the model"\
                    "evaluation"
                    print(warning)
                    outfile.write(warning + "\n\n")              
                
                sscore = silhouette_score(
                        distances, cluster_labels, metric='precomputed')
            
                outfile.write(f'Silhouette Score: {sscore}\n\n')               

            outfile.write(f"{'*'*79} \n")


if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(
                sys.argv[1:], "hr:g:o:",
                ["help", "results=", "gold=", "output="])
        
    except getopt.GetoptError as err:
        print(str(err))
        usage()
        sys.exit(2)    
    
    results_folder = None
    gold_folder = None
    output_file = "evaluation.txt"
    
    for opt, value in opts:
        if opt in ("-h", "--help"):
            help_msg()
            usage()
            sys.exit()            
        elif opt in ("-r", "--results"):            
            if os.path.isdir(value):
                results_folder = value
            else:
                raise ValueError('the "-r" argument expects a directory path')            
        elif opt in ("-g", "--gold"):
            if os.path.isdir(value):
                gold_folder = value
            else:
                raise ValueError('the "-g" argument expects a directory path')
        elif opt in ("-o", "--output"):
            output_file = value
        else:
            raise ValueError('Unhandled option')
                        
    # check if all the non-optional parameters have been passed
    if not all([results_folder, gold_folder]):
        raise IndexError('A directory path is missing')

    # check if the results files in the results folder are properly formatted
    filtered_results = sanity_check(results_folder)
    
    # proper evaluation is performed
    evaluation(filtered_results, gold_folder, output_file)
    
    