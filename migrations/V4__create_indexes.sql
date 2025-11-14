-- user_pastes_with_stats query
CREATE INDEX IF NOT EXISTS idx_pastes_user_id ON pastes(user_id);
CREATE INDEX IF NOT EXISTS idx_comments_paste_id ON comments(paste_id);
CREATE INDEX IF NOT EXISTS idx_likes_paste_id ON likes(paste_id);
CREATE INDEX IF NOT EXISTS idx_paste_tags_paste_id ON paste_tags(paste_id);
CREATE INDEX IF NOT EXISTS idx_paste_folders_paste_id ON paste_folders(paste_id);

-- popular_pastes_by_category query
CREATE INDEX IF NOT EXISTS idx_pastes_category_privacy ON pastes(category_id, privacy_level) 
WHERE privacy_level = 'public';
CREATE INDEX IF NOT EXISTS idx_paste_views_paste_id ON paste_views(paste_id);

-- user_activity_stats query
CREATE INDEX IF NOT EXISTS idx_pastes_user_id_created ON pastes(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_comments_user_id ON comments(user_id);
CREATE INDEX IF NOT EXISTS idx_likes_user_id ON likes(user_id);
CREATE INDEX IF NOT EXISTS idx_paste_views_user_id ON paste_views(user_id);

-- tag_analysis query
CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);
CREATE INDEX IF NOT EXISTS idx_paste_tags_tag_id ON paste_tags(tag_id);
CREATE INDEX IF NOT EXISTS idx_pastes_name_length ON pastes((CHAR_LENGTH(name)));