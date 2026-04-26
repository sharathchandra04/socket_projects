class StateMachine:
    """
    Validates and enforces connection state transitions.
    """

    # -----------------------------
    # Client states
    # -----------------------------
    CLIENT_TRANSITIONS = {
        "READING": {"WAIT_BACKEND", "CLOSED"},
        "WAIT_BACKEND": {"WRITING", "CLOSED"},
        "WRITING": {"CLOSED"},
        "CLOSED": set(),
    }

    # -----------------------------
    # Backend states
    # -----------------------------
    BACKEND_TRANSITIONS = {
        "IDLE": {"BUSY"},
        "BUSY": {"IDLE", "CLOSED"},
        "CLOSED": set(),
    }

    # -----------------------------
    def transition_client(self, conn, new_state):
        self._validate(conn.state, new_state, self.CLIENT_TRANSITIONS)
        conn.state = new_state

    def transition_backend(self, conn, new_state):
        self._validate(conn.state, new_state, self.BACKEND_TRANSITIONS)
        conn.state = new_state

    # -----------------------------
    def _validate(self, current, new, rules):
        allowed = rules.get(current, set())

        if new not in allowed:
            raise Exception(
                f"Invalid state transition: {current} → {new}"
            )