"""
author: Yichen Zhang
"""
import pandas as pd
import numpy as np
from Voting import Voting

class PluralityVoting(Voting):
    
    class PluralityBallot(Voting.Ballot):
        
        def __init__(self, scores):
            super().__init__(scores)
            
        def isValid(self, try_handle_invalid=True):
            # fill missing values with 0
            self.scores.fillna(0, inplace=True)
            # check if self.scores is numeric
            if not np.issubdtype(self.scores.dtype, np.number):
                return False
            # interpret the largest score as the one to vote, if specified to
            if try_handle_invalid:
                self.scores = (self.scores==self.scores.max()).astype(int)
            # check whether the ballot votes for exactly one candidate
            return (self.scores.value_counts()[1]==1 and 
                    self.scores.value_counts()[0]==len(self.scores)-1)
        
        def Vote(self, candidates):
            # vote 1 for one candidate and 0 for everyone else
            return pd.Series([1 if c==self.scores.idxmax() else 0 
                              for c in candidates], index = candidates)
        
        def Export(self, candidates, simple=False):
            # if simple is set to True, will use sparse representation and
            # only record which candidate to vote for
            if simple:
                return self.scores.idxmax()
            else:
                return self.Vote(candidates)
    
    def __init__(self, candidates, try_handle_invalid=True):
        super().__init__(candidates, try_handle_invalid)
    
    def AddBallot(self, new_ballot):
        # support both a string or a Series to represent a vote
        if type(new_ballot)==str:
            ballot = self.PluralityBallot(
                pd.Series([1 if c==new_ballot else 0 for c in self.candidates], 
                          index = self.candidates))
        elif (new_ballot.shape==(1,) and 
              isinstance(new_ballot.iloc[0,], str)):
            # this part handles importing file with simple string format
            ballot = self.PluralityBallot(
                pd.Series([1 if c==new_ballot.iloc[0,] else 0 
                           for c in self.candidates], index = self.candidates))
        else:
            # if some candidates have no score, fill them with 0
            if self.try_handle_invalid:
                new_ballot = new_ballot.copy()
                for c in self.candidates:
                    if c not in new_ballot:
                        new_ballot[c] = 0
            ballot = self.PluralityBallot(new_ballot)
        try:
            if ballot.isValid(self.try_handle_invalid):
                self.ballots.append(ballot)
                return True
            return False
        except:
            return False
    
    def ImportBallots(self, filename):
        return super().ImportBallots(filename)
        
    def ExportBallots(self, filename, simple=False):
        # if simple is set to True, will use sparse representation and
        # only record which candidate to vote for
        if simple:
            df = pd.DataFrame(columns=["candidate"])
            for b in self.ballots:
                df.loc[len(df)] = b.Export(self.candidates, True)
            df.to_excel(filename)
            return df.shape[0]
        else:
            return super().ExportBallots(filename)
    
    def RunElection(self, candidates=None):
        return super().RunElection(candidates)
    
    def SplitSize(self, num_candidates):
        return super().SplitSize(num_candidates)
    