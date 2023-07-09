"""
author: Yichen Zhang
"""
import pandas as pd
import numpy as np
from Voting import Voting

class RankedChoiceVoting(Voting):
    
    class RankedChoiceBallot(Voting.Ballot):
        
        def __init__(self, scores, reverse=False):
            super().__init__(scores)
            self.reverse = reverse
            
        def isValid(self, try_handle_invalid=True, allowed_rank):
            if self.try_handle_invalid:
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
            # converts scores to 
            if try_handle_invalid:
                self.scores.loc[self.scores>score_range[1]] = score_range[1]
                self.scores.loc[self.scores<score_range[0]] = score_range[0]
                # round non-integers, if necessary
                if only_int:
                    self.scores = self.scores.round(0)
            # check whether the ballot satisfy the constraints
            return (self.scores.between(score_range[0], score_range[1]).all() 
                    and (not only_int or self.scores.astype("float").apply(
                    lambda x: x.is_integer()).all()))
        
        def Vote(self, candidates):
            # vote the score corresponding to each candidate
            return self.scores.loc[candidates]
        
        def Export(self, candidates):
            return self.Vote(candidates)
    
    def __init__(self, candidates, try_handle_invalid=True, reverse=False, 
                 allowed_rank=0):
        super().__init__(candidates, try_handle_invalid)
        """
        New Parameters
        reverse : bool, default=False
            default is #1 is the most preferred and #2 the second, etc...
            if set to True, bigger numbers are more preferred instead
        allowed_rank : int, default=0
            each ballot can only list the top allowed_rank favorite candidates
            if set to 0, there is no limit on it
        """
        self.reverse = reverse
        if allowed_rank==0:
            allowed_rank = len(candidates)
        self.allowed_rank = allowed_rank
    
    def AddBallot(self, new_ballot):
        # if some candidates have no score, treat them as most disliked
        if self.try_handle_invalid:
            new_ballot = new_ballot.copy()
            if self.reverse:
                default_score = new_ballot.min()-1
            else:
                default_score = new_ballot.max()+1
            for c in self.candidates:
                if c not in new_ballot:
                    new_ballot[c] = default_score
        ballot = self.ScoreBallot(new_ballot)
        try:
            if ballot.isValid(self.try_handle_invalid, self.reverse, 
                              self.allowed_rank):
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
    