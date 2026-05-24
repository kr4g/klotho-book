# Klotho Book

Interactive Jupyter Book companion to the [Klotho](https://github.com/kr4g/Klotho) toolkit, covering theory and practice of computational music composition. This is a work in progress, but will ultimately cover such topics as foundational graph structures, formal grammars, evolutionary algorithms, quantum fields, and beyond.

You can read the interactive book online — no installation required.

**Read online:** [https://kr4g.github.io/klotho-book/](https://kr4g.github.io/klotho-book/)

## Local development (optional)

The following is only needed if you want to run or modify the notebooks locally.

Install dependencies and Klotho:

```bash
pip install -r binder/requirements.txt
pip install -e /path/to/Klotho
```

Re-execute all notebooks:

```bash
./rebuild_tutorials.sh
```

Build the site locally:

```bash
npm install -g mystmd
myst build --html
```
