"""
author: Yichen Zhang
"""
import pandas as pd
import numpy as np
from Voting import Voting

class TierListVoting(Voting):
    
    class TierListBallot(Voting.Ballot):
        
        def __init__(self, scores, reverse=False):
            super().__init__(scores)
            self.reverse = reverse
            
        def isValid(self, try_handle_invalid=True, allowed_tier=0):
            if try_handle_invalid:
                if self.reverse:
                    default_score = self.scores.min()-1
                else:
                    default_score = self.scores.max()+1
                # treat missing values as most disliked
                self.scores.fillna(default_score, inplace=True)
            # check if there is any missing value
            if self.scores.isna().any():
                return False
            # check if self.scores is numeric
            if not np.issubdtype(self.scores.dtype, np.number):
                return False
            # flip the scores if the score is reversed
            if self.reverse:
                self.scores = self.scores.max()+self.scores.min()-self.scores
            # converts scores to tiers, smaller numbered tier is always 
            # preferred
            if try_handle_invalid:
                self.rank = pd.Series([(self.scores.unique()<self.scores[c])
                                       .sum()+1 for c in self.scores.index], 
                                      index=self.scores.index)
                self.rank.loc[self.rank>allowed_tier] = allowed_tier+1
            else:
                self.rank = self.scores
            # only ties at the lowest rank is allowed (ignored ranks)
            bottom_rank = self.rank.max()
            # check whether the ballot satisfy the constraints
            for i in range(1, bottom_rank+1):
                if self.rank.value_counts()[i] == 0:
                    return False
            return (self.rank.between(1, bottom_rank).all() and 
                    self.rank.astype("float").apply(
                    lambda x: x.is_integer()).all())
        
        def Vote(self, candidates):
            # if all candidates are in the last tier, vote 0 for everyone
            if self.rank.loc[candidates].min()==self.rank.max():
                return pd.Series(0, index=candidates)
            # vote 1 for candidates in the top tier and 0 for everyone else
            return (self.rank==self.rank.loc[candidates].min()).astype(int)
        
        def Export(self, candidates):
            return self.rank
    
    def __init__(self, candidates, try_handle_invalid=True, reverse=False, 
                 allowed_tier=0):
        super().__init__(candidates, try_handle_invalid)
        """
        New Parameters
        reverse : bool, default=False
            default is #1 is the most preferred and #2 the second, etc...
            if set to True, bigger numbers are more preferred instead
        allowed_tier : int, default=0
            the number of tiers each ballot is allowed to list, excluding a 
            default tier at the bottom
            if set to 0, there is no limit on it
        """
        self.reverse = reverse
        if allowed_tier==0:
            allowed_tier = len(candidates)
        self.allowed_tier = allowed_tier
    
    def AddBallot(self, new_ballot):
        # support a string, a list of lists/strings, or a Series 
        # to represent a vote
        if type(new_ballot)==str:
            new_ballot = pd.Series({new_ballot:1})
        elif type(new_ballot)==list:
            new_ballot_copy = new_ballot.copy()
            new_ballot = pd.Series([], dtype="int64")
            # a list of list/strings, each list/string is a tier
            for tier_num, tier_member in enumerate(new_ballot_copy):
                if type(tier_member)==str:
                    # the tier is just one string
                    new_ballot[tier_member] = tier_num+1
                else:
                    # the tier is a list
                    for member in tier_member:
                        new_ballot.loc[member] = tier_num+1
        else:
            new_ballot = new_ballot.copy()
        if self.try_handle_invalid:
            # if some candidates have no score, treat them as most disliked
            if self.reverse:
                default_score = new_ballot.min()-1
            else:
                default_score = new_ballot.max()+1
        else:
            # if some candidates have no score, fill the scores with NaN
            default_score = np.nan
        for c in self.candidates:
            if c not in new_ballot:
                new_ballot[c] = default_score
        ballot = self.TierListBallot(new_ballot, self.reverse)
        try:
            if ballot.isValid(self.try_handle_invalid, self.allowed_tier):
                self.ballots.append(ballot)
                return True
            return False
        except:
            return False
    
    def ImportBallots(self, filename):
        return super().ImportBallots(filename)
        
    def ExportBallots(self, filename):
        return super().ExportBallots(filename)
    
    def RunElection(self, candidates=None):
        return super().RunElection(candidates)
    
    def SplitSize(self, num_candidates):
        return super().SplitSize(num_candidates)
    