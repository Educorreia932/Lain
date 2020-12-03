DROP TABLE IF EXISTS Reactions;

CREATE TABLE Reactions (
    MessageID INT NOT NULL,
    ChannelID INT NOT NULL,
    RoleID INT NOT NULL,
    PRIMARY KEY(MessageID, ChannelID, RoleID)
);

