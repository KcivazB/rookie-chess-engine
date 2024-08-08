class CastleRights:
    def __init__(self, wKs, wQs, bKs, bQs):
        self.wKs = wKs
        self.wQs = wQs
        self.bKs = bKs
        self.bQs = bQs

    def __eq__(self, other):
        if isinstance(other, CastleRights):
            return (self.wKs == other.wKs and self.wQs == other.wQs and
                    self.bKs == other.bKs and self.bQs == other.bQs)
        return False
    
    def __repr__(self):
        return f"CastleRights(wKs={self.wKs}, wQs={self.wQs}, bKs={self.bKs}, bQs={self.bQs})"