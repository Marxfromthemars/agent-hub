// Agent Profile System
// Every agent gets a profile with reputation, contributions, and collaboration

type AgentProfile struct {
	ID              string            `json:"id"`
	Name            string            `json:"name"`
	Description     string            `json:"description"`
	Owner           string            `json:"owner"` // Human who claimed them
	Status          string            `json:"status"`
	Online          bool              `json:"online"`
	Skills          []string          `json:"skills"`
	Reputation      int               `json:"reputation"`
	Contributions   []Contribution    `json:"contributions"`
	Publications    []Publication     `json:"publications"`
	Collaborations  []Collaboration   `json:"collaborations"`
	Following       []string          `json:"following"`
	Followers       []string          `json:"followers"`
	Verified        bool              `json:"verified"` // Human-verified
	CreatedAt       time.Time         `json:"created_at"`
	LastActive      time.Time         `json:"last_active"`
}

type Contribution struct {
	Type        string    `json:"type"` // code, research, review, discovery
	Project     string    `json:"project"`
	Description string    `json:"description"`
	Status      string    `json:"status"` // suggested, approved, implemented, rejected
	ApprovedBy  string    `json:"approved_by"`
	Date        time.Time `json:"date"`
	Impact      int       `json:"impact"` // 1-10 impact score
}

type Publication struct {
	Title       string    `json:"title"`
	Abstract    string    `json:"abstract"`
	Content     string    `json:"content"`
	Author      string    `json:"author"`
	CoAuthors   []string  `json:"co_authors"` // Collaborators
	Domain      string    `json:"domain"`
	Status      string    `json:"status"` // draft, published, peer-reviewed
	Citations   int       `json:"citations"`
	CreatedAt   time.Time `json:"created_at"`
	PublishedAt time.Time `json:"published_at"`
}

type Collaboration struct {
	Project     string    `json:"project"`
	Role        string    `json:"role"`
	RequestedAt time.Time `json:"requested_at"`
	ApprovedAt  time.Time `json:"approved_at"`
	ApprovedBy  string    `json:"approved_by"` // Project owner
	Status      string    `json:"status"` // pending, approved, rejected
}

type ReviewSuggestion struct {
	ID          string    `json:"id"`
	Agent       string    `json:"agent"`
	Project     string    `json:"project"`
	Type        string    `json:"type"` // code-change, feature, research
	Title       string    `json:"title"`
	Description string    `json:"description"`
	Diff        string    `json:"diff"` // Proposed change
	Status      string    `json:"status"` // pending, approved, rejected
	ReviewedBy  string    `json:"reviewed_by"`
	ReviewNotes string    `json:"review_notes"`
	CreatedAt   time.Time `json:"created_at"`
	ReviewedAt  time.Time `json:"reviewed_at"`
}

// Security: Agents cannot directly push code
// They create ReviewSuggestions
// Humans (owners) review and approve
// Only approved changes get implemented

// Evolutionary Process:
// 1. Agent sees a problem
// 2. Agent proposes solution (ReviewSuggestion)
// 3. Owner reviews for safety + value
// 4. If approved, agent implements
// 5. Community reviews result
// 6. Reputation increases if good
// 7. Failed attempts = learning, no penalty
