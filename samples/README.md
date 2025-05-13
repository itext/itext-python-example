This directory contains examples on how to use the iText library within a
Python.NET environment. The Python scripts themselves are located in the
`sandbox` directory.

Files, which start with an `_` are common "library" files and should not be
run directly. Every other Python file is a separate example, which can be
run on its own. Examples will put their output next to the Python scripts
themselves with the same base name.

For example, to run the `paragraph_text_with_style` sample, make sure the
`python` environment you are using has the `itextpy` package installed and
run this command in the terminal:

```shell
python layout/paragraph_text_with_style.py
```

This will create a PDF file at `layout/paragraph_text_with_style.pdf`, where
you can check the results.

To run all the available samples, use the `run_samples.ps1` script on Windows
and the `run_samples.sh` script on *nix.

Most of the samples are based on the .NET iText samples, which can be found at
[itext-publications-samples-dotnet](https://github.com/itext/itext-publications-samples-dotnet).
