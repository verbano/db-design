CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    paste_id INT NOT NULL REFERENCES pastes(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    parent_comment_id INT REFERENCES comments(id) ON DELETE CASCADE
);

CREATE TABLE likes (
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    paste_id INT NOT NULL REFERENCES pastes(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, paste_id)
);

CREATE TABLE paste_views (
    id SERIAL PRIMARY KEY,
    paste_id INT NOT NULL REFERENCES pastes(id) ON DELETE CASCADE,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45)
);

CREATE TABLE paste_proposals (
    id SERIAL PRIMARY KEY,
    original_paste_id INT NOT NULL REFERENCES pastes(id) ON DELETE CASCADE,
    proposed_content TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    created_by INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE TABLE proposal_comments (
    id SERIAL PRIMARY KEY,
    proposal_id INT NOT NULL REFERENCES paste_proposals(id) ON DELETE CASCADE,
    user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    paste_id INT NOT NULL REFERENCES pastes(id) ON DELETE CASCADE,
    reporter_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reason TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'resolved')),
    resolved_at TIMESTAMP
);