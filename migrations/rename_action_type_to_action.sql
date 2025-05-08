-- Rename action_type back to action in auction_history table
ALTER TABLE auction_history RENAME COLUMN action_type TO action;
