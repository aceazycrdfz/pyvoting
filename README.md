# UNDER CONSTRUCTION

THIS README IS NOT FINISHED YET!

# Project Overview
This is an election framework in python that simulates 9 voting methods, including 4 I have invented! In this README document I will explain what all these voting methods are, their recommended practical usage, and how to use my code. In Voting.py, there are documentations for every function in this framework in great detail. 

When this code is used to simulate an election, it will return a list ranking all candidates possibly with tied ranks. So although these voting methods are primarily designed for single winner elections, they can be easily extended to letting the top few candidates win. However, this code is NOT made for elections with proportional representation. As for multi-winner elections, there exists better voting methods that my framework cannot support. 

My code will also attach a log to each candidate, which documents the processes and outcomes of each step in the election. By inspecting this log you can extract the score of each candidate and understand the whole election process (very useful for some complicated voting methods). You can use whatever method you prefer to visualize the election result using the log. Refer to the documentation of the RunElection function in Voting.py for its format (except for STAR Voting, please refer to STARVoting.py for its special log format). 

This code is very robust and versatile. It ranks all candidates and performs tie-breaking exhaustively. It can accept and interpret ballots that doesn't strictly follow the required format. There are many examples for acceptable ballot input when I later introduce the voting methods. 

The OOP nature of this code makes it very easy to develop new voting methods under my framework! All xxxVoting classes inherit the Voting class where the core RunElection function was already inplemented. You can easily design your own voting method by mimicking my implementations of these xxxVoting.py. There are very detailed comments explaining every step in the code. Essentialy, all you need to do is to redefine the Vote function of the your Ballot class. 

# How to Use This Code

...

# Incentives for Elimination Process

(I don't know what to call this because "backward elimination" and "bottom elimination" are terms already used in other scenarios)

Before I proceed to introduce all these voting methods, I will briefly explain why the common RunElection function in the Voting class runs the election by repeatedly eliminating the candidate with the worst score (the SplitSize function is tunable if you define your own voting method). In most election senarios, we care much more about the ranking of the top few candidates than the ranking of the bottom few. Thus, the ranking of the top few candidates needs to be determined with caution and voted with as little distraction as possible. Repeatedly eliminating the candidate at the bottom and does runoff on the rest can achieve this. 

# Plurality Voting

Plurality voting is the simplest and most common voting method: each voter votes for one candidate and the candidate with the most vote wins. It beats every other methods in simplicity and efficiency. 

However, when there exists more than 2 candidates, the winner in plurality voting might not be the one with the broadest support. This is because plurality voting assumes each voter has one favorite candidate and dislikes everyone else equally, which is almost never the reality. The consequence of this is that one might be incentivized to not vote for their favorite candidate when their favorite is unlikely going to win. Plurality voting does not satisfy the property that "if a voter prefers candidate x over candidate y, there should be no incentive to cast a ballot that benefits candidate y more than candidate x" (this concept is similar to "incentive compatibility"), which every other voting methods listed below satisfy. In other words, it is not strategy-proof. 

In my code, the common framework of repeatedly eliminating the bottom candidate is used. But for plurality voting the score for each candidate remains the same across rounds. Therefore, the score in the first entry of the log is the vote earned by that candidate. This is also true for Approval Voting and Score Voting. 

# Approval Voting

Approval voting would've been self-explanatory had it be named multiple-choice voting. It differs from plurality voting only in that one can vote for (approve) as many candidates as possible and still the winner is the one with the most votes (approval). This simple change fixed the main problem of plurality voting: support for the candidates are no longer exclusive. Voting for unpopular candidates does not affect one's opinion on the popular candidates. Therefore, there will be no reason one would ever vote for a less preferred candidate over a perferred one. 

Approval voting still needs the voters to determine the "approving cutoff" in their mind. This process could be a bit strategic but not in a way that makes one lie about their true preferences. 

Overall, approval voting is the simplest and the most efficient among alternative voting methods. 

# Score Voting

What if instead of full approval and not approval one can express something in between? That's where score voting comes in. Voters vote on a scale (say 0 to 5) and the candidate with the highest total score wins. This gives more flexibility to voters comparing to approval voting. 

Voters are not always incentivized to report their true payoffs in score voting. This is not incentive compatible and a counter-example can be easily made. Nonetheless, just like in approval voting, one is never incentivized to give a lower score to a perferred candidate and give a higher score for a less preferred one. 

When using my code, you can specify the acceptable range and whether only integers are allowed. If specified, my code can also help fixing invalid ballots by putting out-of-bound scores back in and round non-integers if necessary. STAR Voting, Normalized Score Voting, and Standardized Score Voting also support these feasures. 

# STAR Voting

STAR stands for "Score then Automatic Runoff". It is very similar to score voting: voters rate all candidates on a scale and candidates are ranked by their total score. On top of this, there is an additional runoff round between the 2 best candidates. In the runoff round, each ballot is considered one vote to the candidate with a higher score. The winner of the runoff round wins the election. 

STAR voting's tie-breaking is difficult in that there are multiple scenarios for ties, although they are rare. The STAR Voting organization listed 2 [official tie-breaking protocals](https://www.starvoting.org/ties), but they are unnatural and hard to implement. In my code I implemented my own tie-breaking method. In the scoring round, all candidates who has strictly less than 2 other candidates with better scores are qualified in the runoff round. So although there are at least 2 qualifiers, there might be more due to ties in scores. Then the runoff round is like approval voting: among all quanlified candidates, each ballot votes for the candidate(s) assigned with the highest score. Ties in the runoff round is broken by the scoring round score. This tie-breaking rule is easy to understand and implement. (In fact, due to the possibllity of ties, STARVoting is the only voting class that implemented its own RunElection function)

advantages

# Ranked Choice Voting

...

# Tier List Voting

...

# Tiered Popularity Voting

...

# Normalized Score Voting

## test

### test

although the support for candidates seems to be in conflict, whenever a candidate is eliminated, its effect on other's scores is gone

# Standardized Score Voting

...