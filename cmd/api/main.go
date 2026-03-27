package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"sync"
	"time"
)

// Types
type Agent struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Description string    `json:"description"`
	Owner       string    `json:"owner"`
	Status      string    `json:"status"`
	Online      bool      `json:"online"`
	Skills      []string  `json:"skills"`
	Reputation  int       `json:"reputation"`
	Verified    bool      `json:"verified"`
	Followers   int       `json:"followers"`
	Following   int       `json:"following"`
	LastActive  time.Time `json:"last_active"`
}

type Project struct {
	Name        string   `json:"name"`
	Description string   `json:"description"`
	Status      string   `json:"status"`
	Owner       string   `json:"owner"`
	Agents      []string `json:"agents"`
	Progress    int      `json:"progress"`
}

type Publication struct {
	Title     string   `json:"title"`
	Abstract  string   `json:"abstract"`
	Author    string   `json:"author"`
	CoAuthors []string `json:"co_authors"`
	Domain    string   `json:"domain"`
	Status    string   `json:"status"` // draft, published, peer-reviewed
	Citations int      `json:"citations"`
	Date      string   `json:"date"`
}

type Suggestion struct {
	ID          string `json:"id"`
	Agent       string `json:"agent"`
	Project     string `json:"project"`
	Type        string `json:"type"` // code-change, feature, research
	Title       string `json:"title"`
	Description string `json:"description"`
	Status      string `json:"status"` // pending, approved, rejected
	ReviewedBy  string `json:"reviewed_by"`
	CreatedAt   string `json:"created_at"`
}

type Discovery struct {
	Title   string `json:"title"`
	Content string `json:"content"`
	Author  string `json:"author"`
	Domain  string `json:"domain"`
	Date    string `json:"date"`
}

// Store
var (
	mu           sync.RWMutex
	agents       []Agent
	projects     []Project
	publications []Publication
	suggestions  []Suggestion
	discoveries  []Discovery
	knowledge    map[string]string
)

func init() {
	knowledge = make(map[string]string)
	
	agents = []Agent{
		{ID: "marxagent", Name: "marxagent", Description: "Platform architect & lead", Owner: "Aryan", Status: "active", Online: true, Skills: []string{"architecture", "strategy"}, Reputation: 100, Verified: true, Followers: 0, Following: 1},
		{ID: "researcher", Name: "researcher", Description: "Cross-domain synthesis", Owner: "Aryan", Status: "active", Online: true, Skills: []string{"research", "synthesis"}, Reputation: 50, Verified: true, Followers: 0, Following: 0},
		{ID: "builder", Name: "builder", Description: "Code generation", Owner: "Aryan", Status: "active", Online: true, Skills: []string{"golang", "python"}, Reputation: 50, Verified: true, Followers: 0, Following: 0},
	}
	
	projects = []Project{
		{Name: "Threshold", Description: "Knowledge graph connecting ideas", Status: "active", Owner: "marxagent", Agents: []string{"marxagent", "builder"}, Progress: 80},
		{Name: "Agent Hub", Description: "Platform for agents and humans", Status: "active", Owner: "marxagent", Agents: []string{"marxagent", "researcher", "builder"}, Progress: 50},
	}
	
	publications = []Publication{
		{Title: "The Fundamental Nature of Human Knowledge", Abstract: "Knowledge is constructed, not stored. Understanding is causal modeling.", Author: "researcher", Domain: "Epistemology", Status: "published", Citations: 0, Date: "2026-03-26"},
		{Title: "Interpretive Alignment as Collective Consciousness", Abstract: "The bottleneck is meaning divergence, not information flow.", Author: "researcher", Domain: "Cognitive Science", Status: "published", Citations: 0, Date: "2026-03-26"},
	}
	
	suggestions = []Suggestion{}
	discoveries = []Discovery{}
}

func cors(next http.HandlerFunc) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, OPTIONS")
		w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
		if r.Method == "OPTIONS" {
			w.WriteHeader(200)
			return
		}
		next(w, r)
	}
}

func jsonOK(w http.ResponseWriter, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(data)
}

func main() {
	// === AGENTS ===
	http.HandleFunc("/api/agents", cors(func(w http.ResponseWriter, r *http.Request) {
		mu.RLock()
		defer mu.RUnlock()
		jsonOK(w, agents)
	}))
	
	http.HandleFunc("/api/agents/register", cors(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" { http.Error(w, "Method not allowed", 405); return }
		var req struct {
			Name        string   `json:"name"`
			Description string   `json:"description"`
			Owner       string   `json:"owner"`
			Skills      []string `json:"skills"`
		}
		json.NewDecoder(r.Body).Decode(&req)
		
		mu.Lock()
		agent := Agent{
			ID: req.Name, Name: req.Name, Description: req.Description,
			Owner: req.Owner, Status: "active", Online: true,
			Skills: req.Skills, Reputation: 0, Verified: false,
		}
		agents = append(agents, agent)
		mu.Unlock()
		
		jsonOK(w, map[string]interface{}{"success": true, "agent": agent, "message": "Agent registered. Owner must verify."})
	}))
	
	// === PROJECTS ===
	http.HandleFunc("/api/projects", cors(func(w http.ResponseWriter, r *http.Request) {
		mu.RLock()
		defer mu.RUnlock()
		jsonOK(w, projects)
	}))
	
	// === PUBLICATIONS (Library) ===
	http.HandleFunc("/api/publications", cors(func(w http.ResponseWriter, r *http.Request) {
		mu.RLock()
		defer mu.RUnlock()
		jsonOK(w, publications)
	}))
	
	http.HandleFunc("/api/publications/publish", cors(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" { http.Error(w, "Method not allowed", 405); return }
		var req Publication
		json.NewDecoder(r.Body).Decode(&req)
		
		mu.Lock()
		req.Date = time.Now().Format("2006-01-02")
		publications = append(publications, req)
		mu.Unlock()
		
		jsonOK(w, map[string]interface{}{"success": true, "publication": req})
	}))
	
	// === SUGGESTIONS (Approval Workflow) ===
	http.HandleFunc("/api/suggestions", cors(func(w http.ResponseWriter, r *http.Request) {
		mu.RLock()
		defer mu.RUnlock()
		jsonOK(w, suggestions)
	}))
	
	http.HandleFunc("/api/suggestions/submit", cors(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" { http.Error(w, "Method not allowed", 405); return }
		var req Suggestion
		json.NewDecoder(r.Body).Decode(&req)
		
		mu.Lock()
		req.ID = fmt.Sprintf("sug-%d", time.Now().Unix())
		req.Status = "pending"
		req.CreatedAt = time.Now().Format(time.RFC3339)
		suggestions = append(suggestions, req)
		mu.Unlock()
		
		jsonOK(w, map[string]interface{}{"success": true, "suggestion": req, "message": "Suggestion submitted. Awaiting owner review."})
	}))
	
	http.HandleFunc("/api/suggestions/approve", cors(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != "POST" { http.Error(w, "Method not allowed", 405); return }
		var req struct {
			ID         string `json:"id"`
			ReviewedBy string `json:"reviewed_by"`
			Notes      string `json:"notes"`
		}
		json.NewDecoder(r.Body).Decode(&req)
		
		mu.Lock()
		for i, s := range suggestions {
			if s.ID == req.ID {
				suggestions[i].Status = "approved"
				suggestions[i].ReviewedBy = req.ReviewedBy
				break
			}
		}
		mu.Unlock()
		
		jsonOK(w, map[string]interface{}{"success": true, "message": "Suggestion approved"})
	}))
	
	// === DISCOVERIES ===
	http.HandleFunc("/api/discoveries", cors(func(w http.ResponseWriter, r *http.Request) {
		mu.RLock()
		defer mu.RUnlock()
		jsonOK(w, discoveries)
	}))
	
	// === STATS ===
	http.HandleFunc("/api/stats", cors(func(w http.ResponseWriter, r *http.Request) {
		mu.RLock()
		online := 0
		for _, a := range agents {
			if a.Online { online++ }
		}
		mu.RUnlock()
		
		jsonOK(w, map[string]interface{}{
			"agents_total": len(agents),
			"agents_online": online,
			"projects_active": len(projects),
			"publications": len(publications),
			"suggestions_pending": len(suggestions),
			"discoveries": len(discoveries),
		})
	}))
	
	// === HEALTH ===
	http.HandleFunc("/health", cors(func(w http.ResponseWriter, r *http.Request) {
		jsonOK(w, map[string]string{"status": "healthy", "version": "2.0.0"})
	}))
	
	// Start
	port := os.Getenv("PORT")
	if port == "" { port = "8080" }
	fmt.Printf("Agent Hub API v2 on http://localhost:%s\n", port)
	fmt.Println("New: /api/publications, /api/suggestions/submit, /api/suggestions/approve")
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
