# Dank Memes 2020

Official repository of [Dank Memes 2020](https://dankmemes2020.fileli.unipi.it/), the shared task on *multimoDal Artefacts recogNition Knowledge for MEMES* at [Evalita 2020](http://www.evalita.it/).

The training and test sets are available on [the task web page](https://dankmemes2020.fileli.unipi.it/?page_id=37).

Please check the guidelines are available both in this repository (cf. `guidelines.pdf`) and on [the task web page](https://dankmemes2020.fileli.unipi.it/?page_id=37) for:

- info concerning the format of the training and test files, as well as of the submission files

- a description of the different task baselines

  


## Dependencies

The `requirements.txt` lists the Python libraries needed to run the evaluation script. To install them, please run:

```
pip install -r requirements.txt
```



## Baselines

The folder `baselines` contains 4 different baselines, one for each task. 

The format of the baselines are identical to those of the submission files. 

> Results should be submitted in CSV files [...] containing the following data fields:
> - "File": filename of the labelled image
> - "Label": predicted label for each image

> Participants willing to compete in the unlabeled version of the third subtask should submit an additional CSV file encoding the pairwise distances between the images of the test set. This file should [...] contain the following data fields:
> - "Image 1": filename of the first image
> - "Image 2": filename of the second image
> - "Distance": pairwise distance between the two images



## Usage






## Contacts

For any enquiries, requests of clarification and or curses, please get in touch with the **Task Organizers**: [Twitter](https://twitter.com/DankMemeEvalita) | [Email](mailto:dankmemesevalita@gmail.com)



## License

[![licensebuttons by-nc-nd](https://licensebuttons.net/l/by-nc-nd/4.0/88x31.png)](https://creativecommons.org/licenses/by-nc-nd/4.0/)