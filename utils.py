class Utils: 
    ranks_to_rows = {"1" : 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1 , "8": 0}

    rows_to_ranks = {v:k for k , v in ranks_to_rows.items()}

    files_to_cols = {"a" : 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6 , "h": 7}

    cols_to_files = {v:k for k , v in files_to_cols.items()}


    def get_chess_notation():
        pass
    
    def get_rank_file(self, row ,col ):
        return self.col_to_files[col] + self.rows_to_ranks[row]