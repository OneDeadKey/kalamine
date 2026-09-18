# Corpus for Layout Analysis

All JSON files have been generated with [kalamine-corpus](https://github.com/OneDeadKey/kalamine-corpus?tab=readme-ov-file).

## `fr` / `en`

Those corpora and stats come from Don Quixote (Cervantes), Gutenberg Project.

## `fra_mixed-typical_2012_1M-sentences`

These stats come from [University of Leipzig](https://wortschatz.uni-leipzig.de/en/download/French#fra_mixed_2012)

### Sources

French Mixed-Typical 2012, 1M sentences file has been extracted, and the
sentence indices have been stripped with `awk '!($1="")' 
fra_mixed-typical_2012_1M/fra_mixed-typical_2012_1M-sentences.txt > 
fra_mixed-typical_2012_1M-sentences.txt`

### Bibtex

```tex
@misc{fra_mixed_2012,
    author = {Leipzig Corpora Collection},
    title = {French mixed corpus based on material from 2012},
    howpublished = {https://corpora.uni-leipzig.de?corpusId=fra_mixed_2012},
    note = {Accessed: 2024-11-09}
}
```
