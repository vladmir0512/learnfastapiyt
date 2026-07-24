class Task:
    def __init__(self, id, title, description, creator_id, assigned_to, status="new", created_at=None, updated_at=None):
        self.id = id
        self.title = title
        self.description = description
        self.creator_id = creator_id
        self.assigned_to = assigned_to
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

