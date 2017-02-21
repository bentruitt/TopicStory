# News App

The News App is a web application for browsing the news at a high level.
Currently the News App has support for the following:
- Browsing crawled articles in the database, either by source or by date
- Clustering of news articles

The next goal is to find disagreements in the news.
The motivation is that if two news articles disagree with each other semantically, it might be because of different biases or even different facts.
By detecting articles with differing facts, it might be possible to search for fake news.

The approach is to use techniques from NLP, in particular textual entailment.
In textual entailment, the data is split into pairs of text fragments, where the first is called the *text* and the second is called the *hypothesis*.
The goal is to predict what the *text* can infer about the *hypothesis*, in particular whether the text is supports the hypothesis (*entailment*),
contradicts the hypothesis (*contradiction*), or there isn't enough information to infer entailment or contradiction (*neutral*).
By training a neural network to predict these three classes on a large training set, this model can then be run pairs of news articles.
If the model outputs *contradiction* for a pair of articles, then we can infer that these articles disagree with each other.

Some resources:
- [Textual entailment Wikipedia page](https://en.wikipedia.org/wiki/Textual_entailment)
- [Stanford NLP page on textual entailment, contains the training data](http://nlp.stanford.edu/projects/snli/)

Some websites are working on fake news detectors, but there doesn't seem to be any projects for finding disagreements in the news.
