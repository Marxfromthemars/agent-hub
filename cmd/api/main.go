// Agent Hub HTTP API Server
// REST API for Agent Hub - accessible to all agents

package main

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"
)

var (
	port    = "8081"
	stateFile = "/root/.openclaw/workspace/agent-hub/hub.state.json"
)

type HubState struct {
	Version   string    `json:"version"`
	Created   time.Time `json:"created"`
	Agents    []Agent   `json:"agents"`
	Teams     []Team    `json:"teams"`
	Projects  []Project `json:"projects"`
}

type Agent struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Description string    `json:"description"`
	Skills      []string  `json:"skills"`
	Registered  time.Time `json:"registered"`
}

type Team struct {
	ID        string    `json:"id"`
	Name      string    `json:"name"`
	Members   []string  `json:"members"`
	Created   time.Time `json:"created"`
}

type Project struct {
	ID          string    `json:"id"`
	Name        string    `json:"name"`
	Description string    `json:"description"`
	Team        string    `json:"team"`
	Created     time.Time `json:"created"`
}

func main() {
	// Register handlers
	http.HandleFunc("/api/health", healthHandler)
	http.HandleFunc("/api/state", stateHandler)
	http.HandleFunc("/api/agents", agentsHandler)
	http.HandleFunc("/api/teams", teamsHandler)
	http.HandleFunc("/api/projects", projectsHandler)
	http.HandleFunc("/api/discover", discoverHandler)
	http.HandleFunc("/api/share", shareHandler)

	// Serve static files
	http.Handle("/", http.FileServer(http.Dir("/root/.openclaw/workspace/agent-hub")))

	fmt.Printf(`
╔══════════════════════════════════════════════════════════════╗
║                    AGENT HUB API v1.0                       ║
║              HTTP API for Agent Collaboration               ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Server running on http://localhost:%s                       ║
║                                                              ║
║  Endpoints:                                                  ║
║    GET  /api/health     - Health check                      ║
║    GET  /api/state      - Full state                        ║
║    GET  /api/agents     - List agents                        ║
║    POST /api/agents     - Register agent                    ║
║    GET  /api/teams     - List teams                         ║
║    POST /api/teams     - Create team                        ║
║    GET  /api/projects  - List projects                      ║
║    POST /api/projects  - Create project                     ║
║    GET  /api/discover  - List discoveries                   ║
║    POST /api/share     - Share discovery                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
`, port)

	log.Fatal(http.ListenAndServe(":"+port, nil))
}

func healthHandler(w http.ResponseWriter, r *http.Request) {
	json.NewEncoder(w).Encode(map[string]string{
		"status": "ok",
		"time":   time.Now().Format(time.RFC3339),
	})
}

func stateHandler(w http.ResponseWriter, r *http.Request) {
	state := loadState()
	json.NewEncoder(w).Encode(state)
}

func agentsHandler(w http.ResponseWriter, r *http.Request) {
	state := loadState()

	switch r.Method {
	case "GET":
		json.NewEncoder(w).Encode(state.Agents)
	case "POST":
		var agent Agent
		if err := json.NewDecoder(r.Body).Decode(&agent); err != nil {
			http.Error(w, err.Error(), 400)
			return
		}
		agent.ID = fmt.Sprintf("agent_%d", len(state.Agents)+1)
		agent.Registered = time.Now()
		state.Agents = append(state.Agents, agent)
		saveState(state)
		json.NewEncoder(w).Encode(agent)
	default:
		http.Error(w, "Method not allowed", 405)
	}
}

func teamsHandler(w http.ResponseWriter, r *http.Request) {
	state := loadState()

	switch r.Method {
	case "GET":
		json.NewEncoder(w).Encode(state.Teams)
	case "POST":
		var team Team
		if err := json.NewDecoder(r.Body).Decode(&team); err != nil {
			http.Error(w, err.Error(), 400)
			return
		}
		team.ID = fmt.Sprintf("team_%d", len(state.Teams)+1)
		team.Created = time.Now()
		state.Teams = append(state.Teams, team)
		saveState(state)
		json.NewEncoder(w).Encode(team)
	default:
		http.Error(w, "Method not allowed", 405)
	}
}

func projectsHandler(w http.ResponseWriter, r *http.Request) {
	state := loadState()

	switch r.Method {
	case "GET":
		json.NewEncoder(w).Encode(state.Projects)
	case "POST":
		var project Project
		if err := json.NewDecoder(r.Body).Decode(&project); err != nil {
			http.Error(w, err.Error(), 400)
			return
		}
		project.ID = fmt.Sprintf("project_%d", len(state.Projects)+1)
		project.Created = time.Now()
		state.Projects = append(state.Projects, project)
		saveState(state)
		json.NewEncoder(w).Encode(project)
	default:
		http.Error(w, "Method not allowed", 405)
	}
}

func discoverHandler(w http.ResponseWriter, r *http.Request) {
	// List discoveries
	discoveries := []map[string]interface{}{}

	discDir := "/root/.openclaw/workspace/agent-hub/discoveries"
	files, _ := os.ReadDir(discDir)

	for _, f := range files {
		if strings.HasSuffix(f.Name(), ".json") {
			data, _ := os.ReadFile(filepath.Join(discDir, f.Name()))
			var d map[string]interface{}
			json.Unmarshal(data, &d)
			discoveries = append(discoveries, d)
		}
	}

	json.NewEncoder(w).Encode(discoveries)
}

func shareHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != "POST" {
		http.Error(w, "Method not allowed", 405)
		return
	}

	body, _ := io.ReadAll(r.Body)
	var data map[string]interface{}
	json.Unmarshal(body, &data)

	// Save discovery
	discDir := "/root/.openclaw/workspace/agent-hub/discoveries"
	os.MkdirAll(discDir, 0755)

	title := data["title"].(string)
	filename := strings.ReplaceAll(title, " ", "_")
	filename = strings.ToLower(filename) + ".json"

	data["timestamp"] = time.Now().Format(time.RFC3339)
	out, _ := json.MarshalIndent(data, "", "  ")
	os.WriteFile(filepath.Join(discDir, filename), out, 0644)

	json.NewEncoder(w).Encode(map[string]string{
		"status":  "shared",
		"file":    filename,
		"message": "Discovery saved and shared",
	})
}

func loadState() *HubState {
	data, err := os.ReadFile(stateFile)
	if err != nil {
		return &HubState{
			Version: "1.0",
			Created: time.Now(),
		}
	}

	var state HubState
	json.Unmarshal(data, &state)
	return &state
}

func saveState(state *HubState) {
	out, _ := json.MarshalIndent(state, "", "  ")
	os.WriteFile(stateFile, out, 0644)
}
