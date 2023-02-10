<br/>
<p align="center">
  <a href="https://github.com/mcpeixoto/PaperRecomenderSystem">
    <img src="https://images.emojiterra.com/google/noto-emoji/v2.034/512px/1f50e.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Paper Recommendation System</h3>

  <p align="center">
    For keeping your sanity when searching for papers.
    <br/>
    <br/>
    <p>View Demo (In the Future)</p>
    .
    <a href="https://github.com/mcpeixoto/PaperRecomenderSystem/issues">Report Bug</a>
    .
    <a href="https://github.com/mcpeixoto/PaperRecomenderSystem/issues">Request Feature</a>
  </p>
</p>


![Contributors](https://img.shields.io/github/contributors/mcpeixoto/PaperRecomenderSystem?color=dark-green) ![Issues](https://img.shields.io/github/issues/mcpeixoto/PaperRecomenderSystem) ![License](https://img.shields.io/github/license/mcpeixoto/PaperRecomenderSystem) ![Forks](https://img.shields.io/github/forks/mcpeixoto/PaperRecomenderSystem?style=social) ![Stargazers](https://img.shields.io/github/stars/mcpeixoto/PaperRecomenderSystem?style=social)

## Table Of Contents

- [Table Of Contents](#table-of-contents)
- [About The Project](#about-the-project)
- [Built With](#built-with)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
  - [Creating A Pull Request](#creating-a-pull-request)
- [License](#license)
- [Authors](#authors)

## About The Project

![Screen Shot](images/screenshot.png)

There are many great README templates available on GitHub, however, I didn't find one that really suit my needs so I created this enhanced one. I want to create a README template so amazing that it'll be the last one you ever need.

Here's why:

* Your time should be focused on creating something amazing. A project that solves a problem and helps others
* You shouldn't be doing the same tasks over and over like creating a README from scratch
* You should element DRY principles to the rest of your life :smile:

Of course, no one template will serve all projects since your needs may be different. So I'll be adding more in the near future. You may also suggest changes by forking this repo and creating a pull request or opening an issue.

A list of commonly used resources that I find helpful are listed in the acknowledgements.

## Built With

This section should list any major frameworks that you built your project using. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.

* [Streamlit](https://streamlit.io/)
* [Facebook's Faiss](https://github.com/facebookresearch/faiss)
* [Sentence Transformers](sentence-transformers/all-mpnet-base-v2)
* [Gensim](https://radimrehurek.com/gensim/index.html)
* [ArXiv dataset](https://www.kaggle.com/Cornell-University/arxiv)

## Getting Started

### Prerequisites

For this project you will need to have installed [Conda](https://docs.conda.io/en/latest/miniconda.html) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html) and have a [Kaggle account](https://www.kaggle.com/).

This also requires ~20Gb of RAM to run and a GPU is recommended
### Installation

1. Install the dependencies

```sh
make install
```

This will use the `environment.yml` file and conda to create a new environment with all the required dependencies.

2. Download the ArXiv dataset from [Kaggle](https://www.kaggle.com/Cornell-University/arxiv), this can be done by running the following command:

```sh
make download
```

Note: This should also download a previosly generated checkpoint for the FaissIndex so you don't have to run the hole thing from scratch. 
TODO

3. Run the following command to create the Faiss index:

```sh
make create_index
```

4. Run the following command to start the Streamlit app:

```sh
make run
```

## Usage

For running the aplicattion, after following the installation steps, run the following command:

```sh
make run
```

If you desire to update the ArXiv dataset and the Faiss index, run the following command:

```sh
make update
```

## Roadmap

- [X] Add Taggs to the papers
- [ ] Provide a way to add the paper to Zotero
- [ ] Add button to find similar papers
- [X] Show the categories
- [X] Show the authors
- [X] Provide a preview of the paper
- [ ] Question Answering to papers

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.
* If you have suggestions for adding or removing projects, feel free to [open an issue](https://github.com/mcpeixoto/PaperRecomenderSystem/issues/new) to discuss it, or directly create a pull request after you edit the *README.md* file with necessary changes.
* Please make sure you check your spelling and grammar.
* Create individual PR for each suggestion.
* Please also read through the [Code Of Conduct](https://github.com/mcpeixoto/PaperRecomenderSystem/blob/main/CODE_OF_CONDUCT.md) before posting your first idea as well.

### Creating A Pull Request

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See [LICENSE](https://github.com/mcpeixoto/PaperRecomenderSystem/blob/main/LICENSE.md) for more information.

## Authors

* [**Miguel Caçador Peixoto**](https://github.com/mcpeixoto/) - *Physics Engineering Student*

