# 1. Project Overview
This is an election framework in python that simulates 9 voting methods, including 4 I have invented! In this README document I will explain what all these voting methods are, their recommended practical usage, and how to use my code. The code is available here: https://github.com/aceazycrdfz/pyvoting

When this code is used to simulate an election, it will return a list ranking all candidates, possibly with tied ranks. My code will also attach a log to each candidate, which documents the processes and outcomes of each step in the election. By inspecting this log you can extract the score of each candidate and understand the whole election process (very useful for some complicated voting methods). You can use whatever method you prefer to visualize the election result using the log. Refer to the documentation of the RunElection function in Voting.py for its format (except for STAR voting, please refer to the STAR voting section for its special log format). 

My code also support both single-winner elections (RunElection) and multi-winner elections (RunMultiWinnerElection), which is great for proportional representation. Although their usage is very similar, there is a distinction and I will thoroughly explain how they work in the Theoretical Motivations section. 

This code is very robust and versatile. It ranks all candidates and performs tie-breaking exhaustively. It can even accept and interpret ballots that doesn't strictly follow the required format. There are many examples for acceptable ballot input when I later introduce the voting methods. 

The OOP nature of this code makes it very easy to develop new voting methods under my framework! All xxxVoting classes inherit the Voting class where the core RunElection function was already inplemented. You can easily design your own voting method by mimicking my implementations of these xxxVoting.py. There are very detailed comments explaining every step in the code. Essentialy, all you need to do is to redefine the Vote function of the your Ballot class. 

# 2. Theoretical Motivations

## 2.1 Incentives for Elimination Process

(I don't know what to call this because "backward elimination" and "bottom elimination" are terms already used in other scenarios)

Before I proceed to introduce all these voting methods, I will briefly explain why the common RunElection function in the Voting class runs the election by repeatedly eliminating the candidate with the worst score (the SplitSize function is tunable if you define your own voting class). In most election senarios, we care much more about the ranking of the top few candidates than the ranking of the bottom few. Thus, the ranking of the top few candidates needs to be determined with caution and voted with as little distraction as possible. Repeatedly eliminating the candidate at the bottom and does runoff on the rest can achieve this. 

The intended effect is that supporters of candidates that got eliminated early have a say in their preferences among the remaining candidates as much as everyone else. Ranked choice voting, tier list voting, tiered popularity voting, normalized score voting, and standardized score voting all have this effect (I invented the later 4 voting methods and they are all thoroughly explained in later sections). 

If you write your own xxxVoting class that inherits the Voting class, you can overwrite the SplitSize function. If your voting methods is also for scenarios that care more about rankings at the top than at the bottom, I recommend not modifying SplitSize. 

## 2.2 How This Code Supports Proportional Representation With Multi-Winner Election

The core RunElection Function orders the candidates by the reverse order of elimination. Therefore, the most straightforward and intuitive way of adapting to a multi-winner scenario is to pick the top few. However, this package uses a better approach: when calling RunMultiWinnerElection, it will repeatedly determine a winner to be at the top by calling RunElection. When a winner from RunElection is found, this candidate will be excluded and all the rest of the candidates will compete for the second place by calling RunElection again. This is done until all the candidates are excluded. Then, the top few returned by RunMultiWinnerElection should be viewed as the winners of the multi-winner election. 

Intuitively the incentive for doing this is that for many voting methods, a vote's support for candidates are not totally independent: more support for one candidate is implicitly less support for others. This is problematic for multi-winner elections (not strategy-proof) because some voters might indicate less support for their favorite because that candidate is guaranteed to win and dedicate their ballot to support contenders for the remaining winning seats. In other words, voters are incentivized to give more support to a less perferred candidate just because they think their preferred candidates can easily win without their support. The mechanism in RunMultiWinnerElection that I described above can fix this issue. Whenever a winner is found, it gets excluded so its effect on voters' support for other candidates are removed. So big supporters of a guaranteed winner have a say in their preferences among the remaining candidates as much as everyone else. 

For plurality voting, approval voting, and score voting, a ballot's score to each candidate is fixed and not affected by the set of candidates in the race. So calling the mechanism in RunMultiWinnerElection cannot help them achieve a desirable multi-winner election. In fact, the rankings produced by RunElection and RunMultiWinnerElection are always the same for most of the voting methods and are mostly the same for all of the voting methods. The later is always much less computationally efficient, especially when the number of candidates and ballots are large. So if a ranking of all candidates is all you need, I don't recommend using RunMultiWinnerElection. 

## 2.3 Spoiler Effect and Spoiler-Proofness

Spoiler effect, or vote splitting, is a common phenomenon in plurality voting elections with more than 2 candidates. It happens when 2 candidates are too similar (they share many common supporters) so when their voters' votes was splitted among them, making them both worse off. 

To formalize spoiler effect on the voting methods, I will define two properties: spoiler-proofness and semi-spoiler-proofness. A spoiler-proof voting method must satisfy the following property: for a arbitrary election, if an arbitrary candidate is duplicated an arbitrary times (by duplicate I mean all voters perfer them equally and ties are broken by coin-toss, if necessary), none of the duplicates is worse off (by "not worse off" I mean if that candidate used to beat another candidate, they still beat them with the existence of duplicates). A semi-spoiler-proof voting method must satisfy the following property: for a arbitrary election, if an arbitrary candidate is duplicated an arbitrary times, not all of the duplicates are worse off (in other words, the best duplicate is not worse off). 

In the discussion of semi-spoiler-proofness I will assume there are no ties, otherwise under my tie-breaking method, there would be a very small chance ranked choice voting and standardized score voting eliminate all duplicates early. To eradicate this small chance, tie-breaking must involve randomness, which I dislike more for a serious election. 

Voting methods that are spoiler-proof: approval voting, score voting, STAR voting, tier list voting, tiered popularity voting, normalized score voting

Voting methods that are semi-spoiler-proof but not spoiler-proof: ranked choice voting, standardized score voting

Voting methods that are neither: plurality voting

# 3. Code Usage Overview

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


# 4. Individual Voting Methods

## 4.1 Plurality Voting

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


## 4.2 Approval Voting

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


## 4.3 Score Voting

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


## 4.4 STAR Voting

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


## 4.5 Ranked Choice Voting

Ranked choice voting (RCV) is my favorite among these alternative voting methods I have introduced so far. Nonetheless, I also consider RCV to have the most number of disadvantages! Later in this section I'll explain RCV's pros and cons, and in the next section I'll explain how tier list voting, which I invented, fixed all the cons. 

In a vanilla RCV, each voter ranks all candidates from the favorite the least favorite. When presented with any subset of candidates, the ballot is treated as a vote for the most preferred candidate in the subset. An RCV election is an elimination process like I explained in the Incentives for Elimination Process section: at first all candidates are included and all ballots vote on them. The candidate(s) with the least score is eliminated (if more than one, will eliminate them all and recursively tie-break on them, refer to my code), and all ballots vote again on the survivors. This is repeated until one candidate is left (equivalently, until one candidate wins more than half vote) and this candidate wins. Because this ranked list ballot automatically votes multiples times, RCV is also called instant runoff voting (IRV). 

(I know I know, no one else introduces RCV like how I just did. But this interpretation fits well with the core idea of this package that ballots are functions that evaluates candidates within any subset of candidates. Once this idea is internalized, it would be very easy to understand the 4 voting methods that I invented.)

RCV can be flexible: a vote can choose to (or be restricted to) only rank a few candidates on their ballot (my code supports both). If all candidates on the ballot are eliminated, this ballot then votes no one. It is easy to see that if we restrict the voters to only rank 1 candidate, this is exactly plurality voting. 

RCV is amazing in that as long as a ballot ranks all candidates, it always votes someone, even after candidates are already eliminated, dropped out, or victorious (for multi-winner elections). In other words, there is never a wasted vote! It is easily provable that as long as a voter is allowed to rank every candidate, there is never incentive to rank a preferred candidate after a less preferred one, so RCV is strategy-proof! It can also easily adapt to multi-winner election using my RunMultiWinnerElection implementation or a more commonly known proportional RCV. 

Unfortunately, RCV has many practical problems. To get a feeling of this, open up the menu of the nearest restaurant and rank all dishes on a paper ballot. The first inconvenience you'll notice is that the ballot size has to be huge. For an optical scannable (machine-readable) RCV ballot in an election of 20 candidates, there needs to be 400 slots! The ballot size rises quadratically ($O(N^2)$ complexity!). If you instead let voters number the candidates, like the Australians do, ballots would have to be processed by human labo(u)r, making an already unbelievably slow RCV election worse. Alternatively, you can restrict the number of candidates each voter can rank, but doing so breaks the very properties all alternative voting methods aims to achieve: strategy-proofness and semi-spoiler-proofness. Just like in plurality voting, if a voter thinks their top few candidates are hopeless, they might choose to not put them on the ballot and instead indicate their preferences on the popular but not favorite candidates. As I mentioned, a plurality voting is just an RCV where each voter can only rank one candidate. 

A typical voter, whether ranking political candidates or dishes, will have a few candidate they really like, one or two they really hate, and many more they don't care or know enough about. Unlike STAR voting and the 4 voting methods I invented, RCV cannot support giving ties, so the voter must decide how to tie-break between candidates they know little about, if they want to put some candidates at the bottom of the list. I doubt anyone can easily tie-break a menu of dishes they neither love nor hate. 

There is another inconvinience for the voters: before filling the ballot, voters must have the complete list in mind. Otherwise, if the voter wants to insert a candidate at a position in the list, they must revise the rank of many candidate already placed (which is the very reason insertion sort is $O(N^2)$). For physical ballots, this can be fixed by providing cards at the voting station to assist the voters. For users of my package, 
my code can perform discretization, parsing the x-th smallest score as the x-th rank, if try_handle_invalid is True. In this way, inserting between two ranks is very easy:to intert between rank 5 and rank 6 you can write 5.5 without changing anything else. 

RCV is actually not spoiler-proof: it is only semi-spoiler-proof. This is because a large number of duplicates will split the ballots placing that candidate on top, thus leading to many duplicates getting eliminated early. It is still semi-spoiler-proof because as the duplicates get eliminated, ballot placing them on top will converge to a few and eventually one duplicate (unless they are very unluckily tied and eliminated together). This duplicate will not be worse-off, comparing to the alternative without the duplicates. 

Spoiler-proofness: NO

Semi-spoiler-proofness: YES

RCV's constructor support these 2 new parameters: 

```python
def __init__(self, candidates, try_handle_invalid=True, reverse=False, 
             allowed_rank=0):
    super().__init__(candidates, try_handle_invalid)
    """
    New Parameters
    reverse : bool, default=False
        default is #1 is the most preferred and #2 the second, etc...
        if set to True, larger numbers are more preferred instead
    allowed_rank : int, default=0
        each ballot can only list the top allowed_rank favorite candidates
        if set to 0, there is no limit on it
    """
```

These 3 voting methods are special in that they treat smaller number as preferred by default (smaller rank = better), contrary to others. By setting reverse to False you can flip it and let larger numbers be preferred instead. This is useful when you want to import ballot files exported by other voting methods. However, no matter the value of reverse, ballots exported from these 3 voting methods are representing preferred candidates with smaller values. Additionally, if reverse is True, then when AddBallot recieves a list it will interpret larger, not smaller, indexes as preferred. Regardless, AddBallot treats candidates missing from the input list as equally disliked the most. 

allowed_rank is the number of candidates each ballot is allowed to rank. The candidates not listed are by default equally disliked the most, so intuitively a ballot can put the candidates in at most allowed_rank+1 tiers. RCV does not allow tied ranks unless they are tied at the bottom. If try_handle_invalid is True and ballot ranked too many candidates, only the top allowed_rank are accepted. Practically speaking, there is no need to set allowed_rank at all if your ballot source (a paper ballot, a google sheet, ...) already restricted the number of ranks. When ballots come from multiple sources and only some are restricting the number of ranks, setting allowed_rank for all ballots makes it fair. 

I especially recommend setting try_handle_invalid to True when using RCV. The following are all possible ways to add a ballot:

```python
import pyvoting
import pandas as pd
election = pyvoting.RankedChoiceVoting(["cand1", "cand2", "cand3"])
# these are all acceptable ballots and will be treated the same
print(election.AddBallot(["cand1", "cand2", "cand3"]))
print(election.AddBallot(["cand1", "cand2"]))
print(election.AddBallot(pd.Series({"cand1":1,
                                    "cand2":2,
                                    "cand3":3})))
print(election.AddBallot(pd.Series({"cand3":9,
                                    "cand2":6,
                                    "cand1":4})))
print(election.AddBallot(pd.Series({"cand1":4,
                                    "cand2":6})))
```


## 4.6 Tier List Voting (original)

(other possible names include ranked choice approval voting, flexible ranked choice voting, ...)

In the last section I thoroughly explained the flaws of RCV. In order to fix them I invented tier list voting (TLV). Despite being similar to RCV, it fixed all its problems. TLV is perfect for many decision-making scenarios, especially political elections. The other 3 original voting methods are not suitable for political purposes. 

Just like the name indicates, in TLV each voter will give a tier list to all candidates. Ideally voters can give as many tiers as possible (possibly one tier for each candidate!), but there could be practical limitations like the ballot size. When presented with any subset of candidates, the ballot votes for the highest tier that contains a presented candidate (since a ballot might vote arbitrarily many candidates per round, TLV can also be called ranked choice approval voting). And just like RCV, the overall format is repeatedly eliminating candidate at the bottom until there's a winner. In other words, the first round is like an approval voting for everyone's top tier. Then as candidates are eliminated, ballots might vote for lower tiers instead. 

Ballot size is no longer a concern for TLV: to prevent the number of slots from growing quadratically, one can limit the number of tiers a voter can give, which still gives voters a high degree of freedom. STAR voting typically lets voters give a score from 0 to 5, taking 5 or 6 slots per candidate, which is a reasonable number of tier for TLV. Still, in an ideal setting, the number of tiers can be unlimited and voters can assign a tier to each candidate, effectively voting an RCV ballot. 

The most significant differene between RCV and TLV is that TLV perfectly supports giving tied ranks. Not only does it gives more freedom to the voters and relieves them from tie-breaking, TLV is spoiler-proof! Recall that RCV is only semi-spoiler-proof because duplicates cannot shre a rank at the top. Now that with tied ranks allowed, no many how many duplicates enter the race, they will share a tier and always get voted for together! 

And TLV is easier to vote than RCV! Just like STAR voting, voters can just "score" candidates one after another without backtracking and inserting incoming candidates to an existing list. 

Spoiler-proofness: YES

Semi-spoiler-proofness: YES

TLV's constructor also supports 2 new parameters. The paramter that controls the number of tier is called allowed_tier instead of allowed_rank from RCV. Other than this difference in names, the usage is exactly the same as the usage of RCV's constructor. 

```python
def __init__(self, candidates, try_handle_invalid=True, reverse=False, 
             allowed_tier=0):
    super().__init__(candidates, try_handle_invalid)
    """
    New Parameters
    reverse : bool, default=False
        default is #1 is the most preferred and #2 the second, etc...
        if set to True, larger numbers are more preferred instead
    allowed_tier : int, default=0
        the number of tiers each ballot is allowed to list, excluding a 
        default tier at the bottom
        if set to 0, there is no limit on it
    """
```

Just like RCV, TLV supports adding a ballot through a pandas.Series or a list of strings. Additionally, TLV accepts a list of tiers, where each tier is a string or a list. 

```python
import pyvoting
import pandas as pd
election = pyvoting.TierListVoting(["cand1", "cand2", "cand3"])
# these are all acceptable ballots and will be treated the same
print(election.AddBallot([["cand1"], ["cand2", "cand3"]]))
print(election.AddBallot(["cand1", ["cand2", "cand3"]]))
print(election.AddBallot(["cand1", [], ["cand2", "cand3"]]))
print(election.AddBallot(pd.Series({"cand1":1,
                                    "cand2":2,
                                    "cand3":2})))
print(election.AddBallot(pd.Series({"cand3":6,
                                    "cand2":6,
                                    "cand1":4})))
```


## 4.7 Tiered Popularity Voting (original)

Tiered popularity voting (TPV) is a variation of TLV that I designed for the purpose of popularity ranking for a very large, possibly hundreds or thousands, number of candidates. For example, anime character popularity ranking is a perfect scenario where TPV works best. 

Just like TLV, in TPV voters put all candidates to a tier list. Since the number of candidates is often too large, most voters will only put a smaller proportion of candidates in the tier list and all other candidates will be put into the default bottom tier. Recall that a ballot is a function or a black box that takes in a subset of candidates and evaluates/votes on them. Instead of voting the best tier among the candidates in TLV, in TPV a ballot votes for all tiers except the bottom tier among the canidates. 

Ranking thousands of characters in the anime world is a challenging voting scenario. [My Anime List](https://myanimelist.net/character.php) ranks the characters by the number of favorites, which is effectively approval voting. Although it is simple and clearly superior to plurality voting, it doesn't give voters enough degrees of freedom to express their opinion: for a huge pool of candidates, a binary score is insufficient to distinguish "know" and "really love". 

[补番目录](https://space.bilibili.com/24055770/video) hosts many monthly rankings of anime and anime characters and they use a better mechanism: candidates are divided into 3 or 5 divisions and an approval voting is hosted within each individual division. The full ranking is produced by appending the ranked results of each division. As a result, a candidate with more votes may be ranked behind another with less votes because they're in a later division, which makes sense because top divisions are more competitive. Then in each division, the top candidate advances to the next division and the bottom one falls back to the lower division next month. The advantage of hosting a seperate approval voting in each tier is voters get to express their opinions to each candidate relative to a smaller group of other candidates, which is why runoffs are commonly used. 

To adapt to such elections, I modified TLV, where ballots vote a small number of candidates they really like, and designed TPV, where ballots vote a much bigger number of candidates they know or sort of like. A typical TPV election is very similar to approval voting when there are a a lot of candidates left. When there are less candidates left, the ballots that put all of them on the tier list  can still express their preference by not voting those at the bottom tier. As a result, the winner of TPV must be known by many voters and must be relatively liked more by other popular candidates at the top. 

The disadvantage of TPV for these kind of voting is that updating results live as new ballots come in is time consuming: unlike approval voting, TPV must run the whole election again to update the result ranking. Nonetheless, this can be overcome by setting a refresh frequency, like once per day. 

Spoiler-proofness: YES

Semi-spoiler-proofness: YES

TPV's usage is exactly the same as TLV. 


## 4.8 Normalized Score Voting (original)

TLV and TPV are invented as improvements to RCV. Ballots in these 3 voting methods always vote 0 or 1 for each candidate, which makes scoring simple. To improve upon score voting and STAR voting, I invented normalized score voting (NSV) and standardized score voting (SSV), where ballots give non-binary scores. 

In NSV and SSV, voters vote exactly the same as in score voting or STAR voting: score each candidate within a range, commonly 0 to 5. However, ballots do not report the exact score of the candidates when they are asked to score a subset of candidates. NSV and SSV follow the same general procedure as RCV, TLV, and TPV: repeatedly eliminate the bottom scoring candidate until there's one left. 

When an NSV ballot is asked to evaluate a subset of candidates, it will first normalize these candidates' scores before returning them. To be precise, the scores of the presented candidates will undergo a linear transformation (shifting + scaling) that turns the maximum score 1 and the minimum score -1. If all these candidates have the same score, all of them will become 0. 

The motive for doing this is to get a better measure of comparative opinion of the candidates. STAR voting does this by adding a runoff round in which the comparative preference of the top 2 candidates are measured equally accross all ballots. NSV takes this idea further by adopting the elimination idea and dynamically normalize the set of scores to equalize every ballot's maximum and minimum. I choose to let the maximum be 1 and minimum be 0 because I intend to let a positive total score represent a relatively preferred candidate and a negative score represent a relatively disliked candidate. The overall support for candidates are close to zero-sum. 

NSV is spoiler-proof. Although the support for candidates seems to be in conflict due to normalization, whenever a candidate is eliminated, its effect on other's scores is gone. The existence of duplicates are not negatively affecting the candidate: the normalization result is only relevant to the maximum and minimum scores so duplicate scores have no effect at all. 

The downside of NSV is that it is very computationally expensive. Therefore, it is only practically feasible when run by computer. Decimal numbers (floating point numbers) are also very common, meaning that floating point errors during computation may produce a wrong result. Fortunately, this is super rare and a one-on-one runoff can do the tie-breaking in case of very close scores. 

Spoiler-proofness: YES

Semi-spoiler-proofness: YES

The usage of NSV is exactly the same as score voting. Please refer to the score voting section on how to use the score_range and only_int parameters. 


## 4.9 Standardized Score Voting (original)

SSV is a variation of NSV, with the same general structure and motivation. The only difference is the SSV ballots will standardize the scores of the selected candidates: a linear transformation (shifting + scaling) that lets the scores to have a mean of 0 and standard deviation of 1. 

This standardization transformation is a better data preprocessing technique than the normalization method in NSV. Unlike NSV, the overall support in each SSV ballot for candidates is exactly zero-sum. Moreover, the standard deviation of scores will be scaled to 1 (in each round), meaning that voters are more incentivized to give a score close to their true preference, since there is no use in polarizing the scores.  

One downside of SSV is that it is not spoiler-proof, like NSV. This is because if a voter really likes a certain candidate (give a positive score), the existence of duplicate will indirectly harm all the scores of all duplicates because the overall mean will be shifted to 0. However, for voters that give negative scores to that candidate, duplicates actually alleviate that negativeness! Therefore, SSV is the only voting method in this package that spoiler candidates could be beneficial! The combined effect should be close to neutural so this is not a concern. Because SSV repeatedly eliminate the bottom candidate, it satisfy semi-spoiler-proofness. 

Spoiler-proofness: NO

Semi-spoiler-proofness: YES

The usage of SSV is exactly the same as score voting and NSV. Please refer to the score voting section on how to use the score_range and only_int parameters. 


# 5. Features Coming Soon

2 parameters each for Normalized Score Voting and Standardized Score Voting

accepts python dictionaries

Round-Rabin voting

