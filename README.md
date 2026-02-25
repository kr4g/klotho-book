# Klotho Book

Interactive Jupyter Book companion to the [Klotho](https://github.com/kr4g/Klotho) toolkit — covering the theory and practice of computer-assisted composition.

**Read online:** [https://kr4g.github.io/klotho-book/](https://kr4g.github.io/klotho-book/)

## Local development

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
