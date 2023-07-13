# VotingSystems Overview
This is a election framework in python that simulates various voting methods, including 4 voting methods I have invented! In this README document I will explain what all these voting methods are, how they work, and their recommended practical usage. For detailed examples of using this code, please refer to main.py. 

This code is very robust and versatile. It ranks all candidates and performs tie-breaking exhaustively. It can accept and interpret ballots that doesn't strictly follow the required format. In main.py there are many examples for acceptable ballot input for each voting method. 

When this code is used to simulate an election, it will return a list ranking all candidates possibly with tied ranks. Each candidate also has a log attached, which documents the processes and outcomes of each step in the election. By inspecting this log you can extract the score of each candidate and understand the whole election process (very useful for some complicated voting methods). You can use whatever method to visualize the election result using the log. Refer to the documentation of the RunElection function in Voting.py for its format (except for STAR Voting, please refer to STARVoting.py for its special log format). 

The OOP nature of this code makes it very easy to develop new voting methods under my framework! All xxxVoting classes inherit the Voting class where the core RunElection function was already inplemented. You can easily design your own voting method by referring to the implementation of PluralityVoting.py and ApprovalVoting.py. Essentialy, all you need is to redefine the Vote function of the your Ballot class. 

# Incentives for Elimination Process

Before I proceed to introduce all these voting methods, I will briefly explain the incentives behind the 