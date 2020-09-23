# Dank Memes 2020

Official repository of the evaluation script and baselines for [Dank Memes 2020](https://dankmemes2020.fileli.unipi.it/), the shared task on *multimoDal Artefacts recogNition Knowledge for MEMES* at [Evalita 2020](http://www.evalita.it/).

The training and test sets are available on [the task web page](https://dankmemes2020.fileli.unipi.it/?page_id=37).

Please check the guidelines are available both in this repository (cf. `guidelines.pdf`) and on [the task web page](https://dankmemes2020.fileli.unipi.it/?page_id=37) for:

- info concerning the format of the training and test files, as well as of the submission files

- a description of the different task baselines

  

## Baselines

The folder `baselines` contains 5 different baselines, one for each task. 

The format of the baselines are identical to those of the submission files. 

> Results should be submitted in CSV files [...] containing the following data fields:
>
> - "File": filename of the labelled image
> - "Label": predicted label for each image

> Participants willing to compete in the unlabeled version of the third subtask should submit an additional CSV file encoding the pairwise distances between the images of the test set. This file should [...] contain the following data fields:
>
> - "Image 1": filename of the first image
> - "Image 2": filename of the second image
> - "Distance": pairwise distance between the two images




## Dependencies

To run the evaluation script you need:

- **Python 3.6+**

- The  lists the libraries in `requirements.txt`. To install them, please run:

```
pip install -r requirements.txt
```



## Usage

The evaluation script can be used to evaluate the results of all the subtasks and runs in one pass by specifying the following arguments:

- the path of the folder containing the result files;

- the path of the folder containing the gold standard files (NOTE: these files should adhere to the same format of the result files and of the baseline files);

- the path of the output file in which the final report will be stored.

  

For instance, in order to evaluate all the results file contained in the `./my_dankmemes_results` folder against the gold standard files contained in `./gold_standards` and to write the report in the `my_performance.txt` file you should run something like:

```bash
python evaluation_dankmemes.py \
--results ./my_dankmemes_results\
--gold ./gold_standards\
--output my_performance.txt
```



This same help message can be printed on screen by passing the `help`argument, as follows:

```bash
python evaluation_dankmemes.py --help
```




## Contacts

For any inquiries, clarifications and/or curses, please get in touch with the **Task Organizers**: [Twitter](https://twitter.com/DankMemeEvalita) | [Email](mailto:dankmemesevalita@gmail.com)



## License

[![licensebuttons by-nc-nd](https://licensebuttons.net/l/by-nc-nd/4.0/88x31.png)](https://creativecommons.org/licenses/by-nc-nd/4.0/)