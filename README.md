# UNDER CONSTRUCTION

THIS README IS NOT FINISHED YET!

# Project Overview
This is an election framework in python that simulates 9 voting methods, including 4 I have invented! In this README document I will explain what all these voting methods are, their recommended practical usage, and how to use my code. The code is available here: https://github.com/aceazycrdfz/pyvoting

When this code is used to simulate an election, it will return a list ranking all candidates, possibly with tied ranks. My code will also attach a log to each candidate, which documents the processes and outcomes of each step in the election. By inspecting this log you can extract the score of each candidate and understand the whole election process (very useful for some complicated voting methods). You can use whatever method you prefer to visualize the election result using the log. Refer to the documentation of the RunElection function in Voting.py for its format (except for STAR voting, please refer to the STAR voting section for its special log format). 

My code also support both single-winner elections (RunElection) and multi-winner elections (RunMultiWinnerElection), which is great for proportional representation. Although their usage is very similar, there is a distinction and I will thoroughly explain how they work in the Theoretical Motivations section. 

This code is very robust and versatile. It ranks all candidates and performs tie-breaking exhaustively. It can even accept and interpret ballots that doesn't strictly follow the required format. There are many examples for acceptable ballot input when I later introduce the voting methods. 

The OOP nature of this code makes it very easy to develop new voting methods under my framework! All xxxVoting classes inherit the Voting class where the core RunElection function was already inplemented. You can easily design your own voting method by mimicking my implementations of these xxxVoting.py. There are very detailed comments explaining every step in the code. Essentialy, all you need to do is to redefine the Vote function of the your Ballot class. 

# Theoretical Motivations

## Incentives for Elimination Process

(I don't know what to call this because "backward elimination" and "bottom elimination" are terms already used in other scenarios)

Before I proceed to introduce all these voting methods, I will briefly explain why the common RunElection function in the Voting class runs the election by repeatedly eliminating the candidate with the worst score (the SplitSize function is tunable if you define your own voting class). In most election senarios, we care much more about the ranking of the top few candidates than the ranking of the bottom few. Thus, the ranking of the top few candidates needs to be determined with caution and voted with as little distraction as possible. Repeatedly eliminating the candidate at the bottom and does runoff on the rest can achieve this. 

The intended effect is that supporters of candidates that got eliminated early have a say in their preferences among the remaining candidates as much as everyone else. Ranked choice voting, tier list voting, tiered popularity voting, normalized score voting, and standardized score voting all have this effect (I invented the later 4 voting methods and they are all thoroughly explained in later sections). 

## How This Code Supports Proportional Representation With Multi-Winner Election

The core RunElection Function orders the candidates by the reverse order of elimination. Therefore, the most straightforward and intuitive way of adapting to a multi-winner scenario is to pick the top few. However, this package uses a better approach: when calling RunMultiWinnerElection, it will repeatedly determine a winner to be at the top by calling RunElection. When a winner from RunElection is found, this candidate will be excluded and all the rest of the candidates will compete for the second place by calling RunElection again. This is done until all the candidates are excluded. Then, the top few returned by RunMultiWinnerElection should be viewed as the winners of the multi-winner election. 

Intuitively the incentive for doing this is that for many voting methods, a vote's support for candidates are not totally independent: more support for one candidate is implicitly less support for others. This is problematic for multi-winner elections (not strategy-proof) because some voters might indicate less support for their favorite because that candidate is guaranteed to win and dedicate their ballot to support contenders for the remaining winning seats. In other words, voters are incentivized to give more support to a less perferred candidate just because they think their preferred candidates can easily win without their support. The mechanism in RunMultiWinnerElection that I described above can fix this issue. Whenever a winner is found, it gets excluded so its effect on voters' support for other candidates are removed. So big supporters of a guaranteed winner have a say in their preferences among the remaining candidates as much as everyone else. 

In fact, the rankings produced by RunElection and RunMultiWinnerElection are always the same for most of the voting methods and are mostly the same for all of the voting methods. The later is always much less computationally efficient, especially when the number of candidates and ballots are large. So if a ranking of all candidates is all you need, I don't recommend using RunMultiWinnerElection. 

## Spoiler Effect and Spoiler-Proofness

Spoiler effect, or vote splitting, is a common phenomenon in plurality voting elections with more than 2 candidates. It happens when 2 candidates are too similar (they share many common supporters) so when their voters' votes was splitted among them, making them both worse off. 

To formalize spoiler effect on the voting methods, I will define two properties: spoiler-proofness and semi-spoiler-proofness. A spoiler-proof voting method must satisfy the following property: for a arbitrary election, if an arbitrary candidate is duplicated an arbitrary times (by duplicate I mean all voters perfer them equally and ties are broken by coin-toss, if necessary), none of the duplicates is worse off (by "not worse off" I mean if that candidate used to beat another candidate, they still beat them with the existence of duplicates). A semi-spoiler-proof voting method must satisfy the following property: for a arbitrary election, if an arbitrary candidate is duplicated an arbitrary times, not all of the duplicates are worse off (in other words, the best duplicate is not worse off). 

Voting methods that are spoiler-proof: approval voting, score voting, STAR voting, tier list voting, tiered popularity voting, normalized score voting

Voting methods that are semi-spoiler-proof but not spoiler-proof: ranked choice voting, standardized score voting

Voting methods that are neither: plurality voting

# Code Usage Overview

To install this package, run this in your command prompt:
```shell
pip install pyvoting
```
This command will install the dependencies (pandas and numpy) as well. 

To update to the latest version, run
```shell
pip install --upgrade pyvoting
```

Now the package is ready to be used in python! 
```python
import pyvoting
```

Since this package is built around the pandas.Series class to represent votes, it is strongly recommended to import the pandas package as well. A few voting methods require the user to use a pandas.Series to represent a vote. 
```python
import pandas as pd
```

You can refer to the pandas.Series documentations [here](https://pandas.pydata.org/docs/reference/api/pandas.Series.html). For the purpose of using this package you just need to know how to initalize a series using a dict, which is very straightforward. Examples in this document should be sufficient for you to understand. 

All voting methods class inherit the abstract Voting class. Below is the documentations for the Voting class. Most of the time, the usage of the specific voting method classes are the same, but I recommend reading the class specific documentations in the next section as there could be extra parameters or other subtle differences. 

The constructor:
```python
def __init__(self, candidates, try_handle_invalid=True):
    """
    Initializes an election using this voting system. 
    
    Parameters
    candidates : list
        an non-empty list of unique strings representing the candidates
    try_handle_invalid : bool, default=True
        whether we attempt to fix ballots that seems invalid
    """
```
I STRONGLY encourage everyone to set try_handle_invalid to be True at all times. For many voting methods, the strict format requires a score specified for every candidate, which can be annoying to the users. Setting this parameter to True grants an unbelievable amount of flexibility when ballots are parsed. In the next section I will give examples of ballots that can be parsed and accepted for each voting method. The specific workflow behind vote parsing is very complicated so I recommend checking out the isValid functions in xxxVoting.py to get an precise understanding of how I preprocess ballots. Don't worry, there are many comments! 

The AddBallot function always accepts a pandas.Series as input, but many voting methods accepts more intuitive and more convinient input formats. The return value immediately reports whether this ballot is accepted. 
```python
def AddBallot(self, new_ballot):
    """
    Adds a ballot to the election if it is valid. 
    
    Parameters
    new_ballot
        a representation of the ballot interpretable by this voting system
    
    Returns
    bool
        whether this ballot is valid and added successfully
    """
```

Aside from calling AddBallot repeatedly, you can also call ImportBallots to import all ballots in an excel spreadsheet to the election. You can call ImportBallots multiple times to import several files or even import the same file multiple times to add duplicated ballots! The ballots should be a pandas.DataFrame, where each column is a candidate and each row a ballot. If you are unsure about the file format, I recommend initializing a dummy election, adding some ballots using AddBallot, then exporting them using ExportBallots as an example. 

It is not guaranteed that all rows in the file are valid ballots. The return value is the number of valid ballots successfully added. 
```python
def ImportBallots(self, filename):
    """
    Imports ballots from an excel spreadsheet to the election. 
    
    Parameters
    filename : str
        name of the ballot file to be imported, possibly the full path
    
    Returns
    int
        number of valid ballots successfully added
    """
```

When using ExportBallots, I strongly recommend exporting to a file with .xlsx extension. All ballots exported are valid and preprocessed, meaning that they might look different from how they were added/imported. All ballots exported without modification are guaranteed to be valid when they are imported with ImportBallots, even when try_handle_invalid is False. 

It is possible to import ballot files exported from a different voting method, but this must be done with caution. One thing to note is that RankedChoiceVoting, TierListVoting, and TieredPopularityVoting treat smaller numbers as preferred by default, contrary to all other voting methods. 
```python
def ExportBallots(self, filename):
    """
    Exports all valid ballots in this election to an excel spreadsheet. 
    
    Parameters
    filename : str
        name of the ballot file to be exported to, possibly the full path
    
    Returns
    int
        number of valid ballots successfully exported
    """
```

The RunElection function is the core of this package. It simulates the whole election using all ballots and a specified subset of candidates. Behind the scene it has a recursive design that thoroughly breaks ties. You can easily construct a [preference matrix](https://www.starvoting.org/preference_matrix) by calling RunElection with each pair of candidates. 

All voting methods except STAR voting uses the log format specified below (refer to the STAR voting section below for its log format). If you are still unsure about the log format, I recommend experimenting with some simple elections and some made-up ballots so that you can inspect the output of RunElection. 

```python
def RunElection(self, candidates=None):
    """
    Runs the election with the given candidates and get the results. 
    
    Parameters
    candidates : list, default=None
        a list of unique strings representing the candidates
        if None, all candidates specified in constructor will be included
    
    Returns
    list
        a list of (candidate, rank, log) tuples representing the election
        result, ordered by rank from first to last, possibly with ties
        log is a list of (score, outcome) tuples each representing the 
        candidate's result of a round of election in chronological order, 
        where outcome can be "u", "l", or "t", representing the candidate
        ended up in the upper bracket, lower bracket, or tied, respectively
    """
```

The RunMultiWinnerElection is in fact very simple: it calls RunElection, put the winner(s) on the top of the result list, exclude the winner(s) then repeat until all candidates are placed. As previously explained, this is a more robust way of running a multi-winner election than picking the top few from RunElection because whenever a winner is selected, its effect on the placement of others is excluded. 

```python
def RunMultiWinnerElection(self, candidates=None):
    """
    Runs a multi-winner election with the given candidates and get the 
    results. 
    
    Parameters
    candidates : list, default=None
        a list of unique strings representing the candidates
        if None, all candidates specified in constructor will be included
    
    Returns
    list
        a list of (candidate, rank, results) tuples representing the 
        election result, ordered by rank from first to last, possibly 
        with ties
        results is a list in RunElection's return format, specifying the
        full election result in which that candidate won, thereby securing
        that rank in the list
    """
```

Here's a typical workflow using this package. This example uses plurality voting. 

```python
import pyvoting
import pandas as pd

# initialize an election with 3 candidates
election = pyvoting.PluralityVoting(["cand1", "cand2", "cand3])

# import ballots from a file
election.ImportBallots("ballot_in.xlsx")

# manually add some ballots
election.AddBallot(pd.Series({"cand1":1,
                              "cand2":0,
                              "cand3":0}))
election.AddBallot(pd.Series({"cand1":1,
                              "cand2":0,
                              "cand3":0}))
election.AddBallot(pd.Series({"cand1":0,
                              "cand2":1,
                              "cand3":0}))

# save all ballots for future use
election.ExportBallots("ballot_out.xlsx")

# run the election and get the result
result = election.RunElection()

# do something with the result...
```


# Individual Voting Methods

## Plurality Voting

Plurality voting is the simplest and most common voting method: each voter votes for one candidate and the candidate with the most vote wins. It beats every other methods in simplicity and efficiency. 

However, when there exists more than 2 candidates, the winner in plurality voting might not be the one with the broadest support. This is because plurality voting assumes each voter has one favorite candidate and dislikes everyone else equally, which is almost never the reality. The consequence of this is that one might be incentivized to not vote for their favorite candidate when their favorite is unlikely going to win. Plurality voting does not satisfy the property that "if a voter prefers candidate x over candidate y, there should be no incentive to cast a ballot that benefits candidate y more than candidate x" (this concept is similar to "incentive compatibility"), which every other voting methods listed below satisfy. In other words, it is not strategy-proof. 

In my code, the common framework of repeatedly eliminating the bottom candidate is used. But for plurality voting the score for each candidate remains the same across rounds. Therefore, the score in the first entry of the log is the vote earned by that candidate. This is also true for Approval Voting and Score Voting. 

Spoiler-proofness: NO
Semi-spoiler-proofness: NO

The PluralityVoting class accepts both a pandas.Series or just a string of the preferred ballot as the one to vote for. 

```python
import pyvoting
import pandas as pd
election = pyvoting.PluralityVoting(["cand1", "cand2", "cand3"])
# these are acceptable ballots for cand1
election.AddBallot("cand1")
election.AddBallot(pd.Series({"cand1":1,
                              "cand2":0,
                              "cand3":0}))
election.AddBallot(pd.Series({"cand3":0,
                              "cand2":0,
                              "cand1":1}))
# these are acceptable ballots for cand1 only when try_handle_invalid 
# is True
election.AddBallot(pd.Series({"cand1":1})
election.AddBallot(pd.Series({"cand1":100.1,
                              "cand2":2.33}))
election.AddBallot(pd.Series({"cand2":-2,
                              "cand3":-5}))
```

Moreover, PluralityVoting supports exporting ballots in sparse representation: only one column for each ballot recording the candidate string to vote for. You can do this by setting the parameter simple to True when calling ExportBallots. 

```python
election.ExportBallots("ballot_out.xlsx", simple=True)
```

ImportBallots can accept ballot files in either format. It will automatically detect the file format. 


## Approval Voting

Approval voting would've been self-explanatory had it be named multiple-choice voting. It differs from plurality voting only in that one can vote for (approve) as many candidates as possible and still the winner is the one with the most votes (approval). This simple change fixed the main problem of plurality voting: support for the candidates are no longer exclusive. Voting for unpopular candidates does not affect one's opinion on the popular candidates. Therefore, there will be no reason one would ever vote for a less preferred candidate over a perferred one. Approval voting still needs the voters to determine the "approving cutoff" in their mind. This process could be a bit strategic but not in a way that makes one lie about their true preferences. 

Overall, approval voting is the simplest and the most efficient among alternative voting methods. 

Spoiler-proofness: YES
Semi-spoiler-proofness: YES

The ApprovalVoting class also supports just a string as a vote. Additionally, it supports a list of strings of candidates to vote for as a ballot. It even accepts an empty list representing voting no one, which PluralityVoting does not. 

```python
import pyvoting
import pandas as pd
election = pyvoting.ApprovalVoting(["cand1", "cand2", "cand3"])
# these are acceptable ballots for cand1
election.AddBallot("cand1")
election.AddBallot(["cand1"])
# these are acceptable ballots for cand1 and cand2
election.AddBallot(["cand1", "cand2"])
election.AddBallot(pd.Series({"cand1":1,
                              "cand2":1,
                              "cand3":0}))
# these are acceptable ballots for cand1 and cand2 only when 
# try_handle_invalid is True
election.AddBallot(pd.Series({"cand1":1,
                              "cand2":1}))
election.AddBallot(pd.Series({"cand1":20,
                              "cand2":20,
                              "cand3":3}))
```


## Score Voting

What if instead of full approval and not approval one can express something in between? That's where score voting comes in. Voters vote on a scale (say 0 to 5) and the candidate with the highest total score wins. This gives more flexibility to voters comparing to approval voting. 

Voters are not always incentivized to report their true payoffs in score voting. This is not incentive compatible and a counter-example can be easily made. Nonetheless, just like in approval voting, one is never incentivized to give a lower score to a perferred candidate and give a higher score for a less preferred one. 

Spoiler-proofness: YES
Semi-spoiler-proofness: YES

When using my code, you can specify the acceptable range and whether only integers are allowed. If specified, my code can also help fixing invalid ballots by putting out-of-bound scores back in and round non-integers if necessary. STAR Voting, Normalized Score Voting, and Standardized Score Voting also support these feasures. 

```python
def __init__(self, candidates, try_handle_invalid=True, score_range=(0, 5), 
             only_int=True):
    super().__init__(candidates, try_handle_invalid)
    """
    New Parameters
    score_range : tuple, default=(0, 5)
        an integer tuple representing the lower bound and the upper bound 
        of the scores, both inclusive
    only_int : bool, default=True
        whether only integer scores is allowed
    """
```

```python
import pyvoting
import pandas as pd
election = pyvoting.ScoreVoting(["cand1", "cand2", "cand3"],
                                score_range=(0, 5), only_int=True)
election.AddBallot(pd.Series({"cand1":0,
                              "cand2":2,
                              "cand3":5}))
# if try_handle_invalid is True, the following is another way of adding 
# a ballot that is exactly the same as above
election.AddBallot(pd.Series({"cand1":-1,
                              "cand2":1.8,
                              "cand3":7}))
```


## STAR Voting

STAR stands for "Score then Automatic Runoff". It is very similar to score voting: voters rate all candidates on a scale and candidates are ranked by their total score. On top of this, there is an additional runoff round between the 2 best candidates. In the runoff round, each ballot is considered one vote to the candidate with a higher score. The winner of the runoff round wins the election. 

STAR voting's tie-breaking is difficult in that there are multiple scenarios for ties, although they are rare. The STAR Voting organization listed 2 [official tie-breaking protocals](https://www.starvoting.org/ties), but they are unnatural and hard to implement. In my code I implemented my own tie-breaking method. In the scoring round, all candidates who has strictly less than 2 other candidates with better scores are qualified in the runoff round. So although there are at least 2 qualifiers, there might be more due to ties in scores. Then the runoff round is like approval voting: among all quanlified candidates, each ballot votes for the candidate(s) assigned with the highest score. Ties in the runoff round is broken by the scoring round score. This tie-breaking rule is easy to understand and implement. (In fact, due to the possibllity of ties, STARVoting is the only voting class that implemented its own RunElection function)

STAR voting and ranked choice voting often compete for the best and most popular alternative voting method. While STAR voting almost always produces the same winner as ranked choice voting (as well as the 4 voting methods I have invented), it is significantly faster to run and simpler to explain. It also support giving tied scores while the vanilla RCV cannot. When the number of candidates is large, RCV's ballot size rises quadratically while STAR voting's ballot size rises linearly (if RCV restricts the number of candidates to rank, it will lose its strategy-proofness and semi-spoiler-proofness!). Therefore, STAR voting is a great tradeoff between rule complexity and top-candidate runoffs. 

Spoiler-proofness: YES
Semi-spoiler-proofness: YES

Just like ScoreVoting, STARVoting's constructor takes in two additional optional parameters: score_range and Only_int. Adding ballots for STARVoting is also exactly the same as ScoreVoting. Please refer to the examples at the end of the ScoreVoting section. 

The RunElection function of STARVoting has a special log format. Naturally, this also affects the result of RunMultiWinnerElection. 

```python
def RunElection(self, candidates=None):
    """
    This STAR voting implementation uses a different tie-breaking protocal 
    that makes more sense and is easier to implement than the typical STAR 
    voting tie-breaking methods!
    
    The log in the returned list has a different format: a numeric tuple 
    (s1, s2) where s1 is the scoring round score and s2 is the runoff 
    round score. Those who did not make it to runoff has a runoff score 0. 
    """
```


## Ranked Choice Voting

...

## Tier List Voting (original)

(other possible names include ranked choie approval voting, flexible ranked choice voting...)

...

## Tiered Popularity Voting (original)

...

## Normalized Score Voting (original)


although the support for candidates seems to be in conflict, whenever a candidate is eliminated, its effect on other's scores is gone

## Standardized Score Voting (original)

...

# Features Coming Soon

2 parameters each for Normalized Score Voting and Standardized Score Voting

