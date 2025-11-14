DROP INDEX IF EXISTS idx_pastes_name_length;
DROP INDEX IF EXISTS idx_paste_tags_tag_id;
DROP INDEX IF EXISTS idx_tags_name;

DROP INDEX IF EXISTS idx_paste_views_user_id;
DROP INDEX IF EXISTS idx_likes_user_id;
DROP INDEX IF EXISTS idx_comments_user_id;
DROP INDEX IF EXISTS idx_pastes_user_id_created;

DROP INDEX IF EXISTS idx_paste_views_paste_id;
DROP INDEX IF EXISTS idx_pastes_category_privacy;

DROP INDEX IF EXISTS idx_paste_folders_paste_id;
DROP INDEX IF EXISTS idx_paste_tags_paste_id;
DROP INDEX IF EXISTS idx_likes_paste_id;
DROP INDEX IF EXISTS idx_comments_paste_id;
DROP INDEX IF EXISTS idx_pastes_user_id;