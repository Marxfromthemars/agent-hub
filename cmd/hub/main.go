// AGENT HUB CLI - Platform for AI agents to build, collaborate, and create
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

var version = "1.0.0"

type (
	Agent struct {
		ID          string    `json:"id"`
		Name        string    `json:"name"`
		Role        string    `json:"role"`
		Parent      string    `json:"parent,omitempty"`
		Projects    []string  `json:"projects"`
		Knowledge   []string  `json:"knowledge"`
		Created     time.Time `json:"created"`
		LastActive  time.Time `json:"last_active"`
		Status      string    `json:"status"` // active, idle, completed
	}

	Team struct {
		ID        string   `json:"id"`
		Name      string   `json:"name"`
		Agents    []string `json:"agents"`
		Goal      string   `json:"goal"`
		Projects  []string `json:"projects"`
		Created   time.Time `json:"created"`
	}

	Company struct {
		ID          string    `json:"id"`
		Name        string    `json:"name"`
		Mission     string    `json:"mission"`
		Agents      []string  `json:"agents"`
		Projects    []string  `json:"projects"`
		Knowledge   []string  `json:"knowledge"`
		Created     time.Time `json:"created"`
	}

	Discovery struct {
		ID        string    `json:"id"`
		Type      string    `json:"type"` // breakthrough, truth, technique
		Content   string    `json:"content"`
		Source    string    `json:"source"`
		Created   time.Time `json:"created"`
	}

	Project struct {
		ID          string    `json:"id"`
		Name        string    `json:"name"`
		Status      string    `json:"status"` // active, paused, completed
		Agents      []string  `json:"agents"`
		Goal        string    `json:"goal"`
		Knowledge   []string  `json:"knowledge"`
		Created     time.Time `json:"created"`
		LastUpdate  time.Time `json:"last_update"`
	}

	HubState struct {
		Version     string            `json:"version"`
		Updated     time.Time         `json:"updated"`
		Agents      map[string]*Agent `json:"agents"`
		Teams       map[string]*Team  `json:"teams"`
		Companies   map[string]*Company `json:"companies"`
		Discoveries []Discovery        `json:"discoveries"`
		Projects    map[string]*Project `json:"projects"`
	}
)

func main() {
	if len(os.Args) < 2 {
		showHelp()
		return
	}

	command := os.Args[1]

	switch command {
	case "spawn":
		handleSpawn(os.Args[2:])
	case "list":
		handleList(os.Args[2:])
	case "status":
		handleStatus(os.Args[2:])
	case "project":
		handleProject(os.Args[2:])
	case "team":
		handleTeam(os.Args[2:])
	case "company":
		handleCompany(os.Args[2:])
	case "discover":
		handleDiscover(os.Args[2:])
	case "knowledge":
		handleKnowledge(os.Args[2:])
	case "work":
		handleWork(os.Args[2:])
	case "shell":
		handleShell()
	case "help", "--help", "-h":
		showHelp()
	default:
		fmt.Printf("Unknown command: %s\n", command)
		showHelp()
	}
}

func showHelp() {
	fmt.Println(`
╔══════════════════════════════════════════════════════════════╗
║                      AGENT HUB v1.0                         ║
║          Platform for AI Agents to Build & Collaborate      ║
║                                                               ║
║  Commands:                                                    ║
║    spawn [name] [role]     - Create a new agent              ║
║    list [agents|teams|companies|projects] - List all         ║
║    status [agent]          - Show agent status              ║
║    project [create|list|work] [args] - Manage projects       ║
║    team [create|add|list] [args] - Manage teams             ║
║    company [create|list] [args] - Manage companies          ║
║    discover [type] [content] - Record a discovery           ║
║    knowledge [query]       - Search shared knowledge         ║
║    work [project] [task]   - Work on a project task          ║
║    shell                   - Interactive hub shell           ║
║                                                               ║
║  Examples:                                                    ║
║    hub spawn mario builder                                   ║
║    hub list agents                                           ║
║    hub project create myapp                                  ║
║    hub discover truth "knowledge compounds through emergence"║
║    hub knowledge compound                                    ║
╚══════════════════════════════════════════════════════════════╝
`)
}

func hubPath() string {
	return "/root/.openclaw/workspace/agent-hub"
}

func statePath() string {
	return filepath.Join(hubPath(), "hub.state.json")
}

func loadState() *HubState {
	state := &HubState{
		Version:  "1.0",
		Updated:  time.Now(),
		Agents:   make(map[string]*Agent),
		Teams:    make(map[string]*Team),
		Companies: make(map[string]*Company),
		Projects:  make(map[string]*Project),
	}

	data, err := os.ReadFile(statePath())
	if err != nil {
		return state
	}

	json.Unmarshal(data, &state)
	return state
}

func saveState(state *HubState) {
	state.Updated = time.Now()
	data, _ := json.MarshalIndent(state, "", "  ")
	os.WriteFile(statePath(), data, 0644)
}

func nextAgentID(state *HubState) string {
	return fmt.Sprintf("agent_%d", len(state.Agents)+1)
}

func nextProjectID(state *HubState) string {
	return fmt.Sprintf("project_%d", len(state.Projects)+1)
}

// Handlers
func handleSpawn(args []string) {
	if len(args) < 2 {
		fmt.Println("Usage: hub spawn [name] [role]")
		return
	}

	name := args[0]
	role := args[1]

	state := loadState()
	agent := &Agent{
		ID:         nextAgentID(state),
		Name:       name,
		Role:       role,
		Projects:   []string{},
		Knowledge:  []string{},
		Created:    time.Now(),
		LastActive: time.Now(),
		Status:     "active",
	}

	state.Agents[agent.ID] = agent
	saveState(state)

	fmt.Printf("%s Agent '%s' (role: %s) spawned as %s\n",
		color("green", "✓"), name, role, agent.ID)
}

func handleList(args []string) {
	if len(args) == 0 {
		showHelp()
		return
	}

	what := args[0]
	state := loadState()

	switch what {
	case "agents":
		fmt.Println(color("cyan", "═══ AGENTS ═══"))
		if len(state.Agents) == 0 {
			fmt.Println("  No agents yet. Spawn one with 'hub spawn [name] [role]'")
			return
		}
		for id, a := range state.Agents {
			fmt.Printf("  %s (%s) - %s - %s\n",
				color("green", a.Name), a.Role, a.Status, id)
		}

	case "teams":
		fmt.Println(color("cyan", "═══ TEAMS ═══"))
		if len(state.Teams) == 0 {
			fmt.Println("  No teams yet.")
			return
		}
		for _, t := range state.Teams {
			fmt.Printf("  %s - Goal: %s - Agents: %d\n",
				color("yellow", t.Name), t.Goal, len(t.Agents))
		}

	case "companies":
		fmt.Println(color("cyan", "═══ COMPANIES ═══"))
		if len(state.Companies) == 0 {
			fmt.Println("  No companies yet.")
			return
		}
		for _, c := range state.Companies {
			fmt.Printf("  %s - Mission: %s - Agents: %d\n",
				color("gold", c.Name), c.Mission, len(c.Agents))
		}

	case "projects":
		fmt.Println(color("cyan", "═══ PROJECTS ═══"))
		if len(state.Projects) == 0 {
			fmt.Println("  No projects yet.")
			return
		}
		for _, p := range state.Projects {
			fmt.Printf("  %s - %s - Agents: %d\n",
				color("green", p.Name), p.Status, len(p.Agents))
		}

	default:
		fmt.Printf("Unknown type: %s\n", what)
	}
}

func handleStatus(args []string) {
	if len(args) == 0 {
		// Show overall hub status
		state := loadState()
		fmt.Println(color("gold", "╔══════════════════════════════════════════════════════════════╗"))
		fmt.Println(color("gold", "║                    HUB STATUS                                ║"))
		fmt.Println(color("gold", "╚══════════════════════════════════════════════════════════════╝"))
		fmt.Printf("\n")
		fmt.Printf("  Agents:     %d\n", len(state.Agents))
		fmt.Printf("  Teams:      %d\n", len(state.Teams))
		fmt.Printf("  Companies:  %d\n", len(state.Companies))
		fmt.Printf("  Projects:   %d\n", len(state.Projects))
		fmt.Printf("  Discoveries: %d\n", len(state.Discoveries))
		fmt.Printf("\n")
		return
	}

	// Show specific agent status
	name := args[0]
	state := loadState()

	for _, a := range state.Agents {
		if strings.ToLower(a.Name) == strings.ToLower(name) {
			fmt.Printf("%s Status for agent '%s'\n", color("cyan", "→"), a.Name)
			fmt.Printf("  ID:     %s\n", a.ID)
			fmt.Printf("  Role:   %s\n", a.Role)
			fmt.Printf("  Status: %s\n", a.Status)
			fmt.Printf("  Projects (%d): %s\n", len(a.Projects), strings.Join(a.Projects, ", "))
			fmt.Printf("  Created: %s\n", a.Created.Format("2006-01-02 15:04"))
			fmt.Printf("  Active:  %s\n", a.LastActive.Format("2006-01-02 15:04"))
			return
		}
	}

	fmt.Printf("Agent '%s' not found\n", name)
}

func handleProject(args []string) {
	if len(args) < 1 {
		fmt.Println("Usage: hub project [create|list|work] [args]")
		return
	}

	action := args[0]
	state := loadState()

	switch action {
	case "create":
		if len(args) < 2 {
			fmt.Println("Usage: hub project create [name]")
			return
		}
		name := args[1]
		goal := ""
		if len(args) > 2 {
			goal = strings.Join(args[2:], " ")
		}

		project := &Project{
			ID:         nextProjectID(state),
			Name:       name,
			Status:     "active",
			Agents:     []string{},
			Goal:       goal,
			Knowledge:  []string{},
			Created:    time.Now(),
			LastUpdate: time.Now(),
		}

		state.Projects[project.ID] = project
		saveState(state)

		fmt.Printf("%s Project '%s' created\n", color("green", "✓"), name)

	case "list":
		handleList([]string{"projects"})

	case "work":
		if len(args) < 4 {
			fmt.Println("Usage: hub project work [project] [task]")
			return
		}
		projName := args[2]
		task := strings.Join(args[3:], " ")

		var project *Project
		for _, p := range state.Projects {
			if p.Name == projName {
				project = p
				break
			}
		}

		if project == nil {
			fmt.Printf("Project '%s' not found\n", projName)
			return
		}

		fmt.Printf("%s Working on '%s': %s\n", color("cyan", "→"), project.Name, task)
		project.Knowledge = append(project.Knowledge, task)
		project.LastUpdate = time.Now()
		saveState(state)

		fmt.Printf("%s Task added to project\n", color("green", "✓"))

	default:
		fmt.Printf("Unknown action: %s\n", action)
	}
}

func handleTeam(args []string) {
	if len(args) < 1 {
		fmt.Println("Usage: hub team [create|add|list] [args]")
		return
	}

	action := args[0]
	state := loadState()

	switch action {
	case "create":
		if len(args) < 2 {
			fmt.Println("Usage: hub team create [name]")
			return
		}
		name := args[1]
		goal := ""
		if len(args) > 2 {
			goal = strings.Join(args[2:], " ")
		}

		team := &Team{
			ID:       fmt.Sprintf("team_%d", len(state.Teams)+1),
			Name:     name,
			Agents:   []string{},
			Goal:     goal,
			Projects: []string{},
			Created:  time.Now(),
		}

		state.Teams[team.ID] = team
		saveState(state)

		fmt.Printf("%s Team '%s' created\n", color("green", "✓"), name)

	case "list":
		handleList([]string{"teams"})

	default:
		fmt.Printf("Unknown action: %s\n", action)
	}
}

func handleCompany(args []string) {
	if len(args) < 1 {
		fmt.Println("Usage: hub company [create|list] [args]")
		return
	}

	action := args[0]
	state := loadState()

	switch action {
	case "create":
		if len(args) < 2 {
			fmt.Println("Usage: hub company create [name]")
			return
		}
		name := args[1]
		mission := ""
		if len(args) > 2 {
			mission = strings.Join(args[2:], " ")
		}

		company := &Company{
			ID:       fmt.Sprintf("company_%d", len(state.Companies)+1),
			Name:     name,
			Mission:  mission,
			Agents:   []string{},
			Projects: []string{},
			Knowledge: []string{},
			Created:  time.Now(),
		}

		state.Companies[company.ID] = company
		saveState(state)

		fmt.Printf("%s Company '%s' created\n", color("green", "✓"), name)

	case "list":
		handleList([]string{"companies"})

	default:
		fmt.Printf("Unknown action: %s\n", action)
	}
}

func handleDiscover(args []string) {
	if len(args) < 2 {
		fmt.Println("Usage: hub discover [type] [content]")
		return
	}

	discType := args[0]
	content := strings.Join(args[1:], " ")

	state := loadState()

	discovery := Discovery{
		ID:      fmt.Sprintf("discovery_%d", len(state.Discoveries)+1),
		Type:    discType,
		Content: content,
		Source:  "agent",
		Created: time.Now(),
	}

	state.Discoveries = append(state.Discoveries, discovery)
	saveState(state)

	fmt.Printf("%s Discovery recorded: %s\n", color("green", "✓"), discType)
	fmt.Printf("  %s\n", truncate(content, 60))
}

func handleKnowledge(args []string) {
	state := loadState()

	if len(args) == 0 {
		// List all knowledge
		fmt.Println(color("cyan", "═══ SHARED KNOWLEDGE ═══"))

		// From discoveries
		if len(state.Discoveries) > 0 {
			fmt.Println(color("yellow", "Discoveries:"))
			for _, d := range state.Discoveries {
				fmt.Printf("  [%s] %s\n", d.Type, truncate(d.Content, 50))
			}
		}

		// From projects
		if len(state.Projects) > 0 {
			fmt.Println(color("yellow", "\nProject Knowledge:"))
			for _, p := range state.Projects {
				if len(p.Knowledge) > 0 {
					fmt.Printf("  %s: %s\n", p.Name, truncate(strings.Join(p.Knowledge, "; "), 50))
				}
			}
		}

		return
	}

	// Search
	query := strings.ToLower(strings.Join(args, " "))
	fmt.Printf("Searching for: %s\n\n", query)

	var results []string
	for _, d := range state.Discoveries {
		if strings.Contains(strings.ToLower(d.Content), query) {
			results = append(results, fmt.Sprintf("[%s] %s", d.Type, d.Content))
		}
	}

	if len(results) == 0 {
		fmt.Println("No results found.")
	} else {
		fmt.Println(color("green", "Results:"))
		for _, r := range results {
			fmt.Printf("  → %s\n", truncate(r, 70))
		}
	}
}

func handleWork(args []string) {
	if len(args) < 2 {
		fmt.Println("Usage: hub work [project] [task]")
		return
	}

	projectName := args[0]
	task := strings.Join(args[1:], " ")

	state := loadState()

	var project *Project
	for _, p := range state.Projects {
		if p.Name == projectName {
			project = p
			break
		}
	}

	if project == nil {
		fmt.Printf("Project '%s' not found. Create it first with 'hub project create %s'\n", projectName, projectName)
		return
	}

	project.Knowledge = append(project.Knowledge, task)
	project.LastUpdate = time.Now()
	saveState(state)

	fmt.Printf("%s Working on %s: %s\n", color("cyan", "→"), projectName, task)
}

func handleShell() {
	fmt.Println(color("gold", `
╔══════════════════════════════════════════════════════════════╗
║                 AGENT HUB SHELL                             ║
║     Type 'exit' to leave, 'help' for commands              ║
╚══════════════════════════════════════════════════════════════╝
`))

	// Simple shell using this binary as REPL
	cmd := exec.Command("./hub")
	cmd.Dir = hubPath()
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	cmd.Run()
}

// Helpers
func truncate(s string, maxLen int) string {
	if len(s) <= maxLen {
		return s
	}
	return s[:maxLen-3] + "..."
}

var colors = map[string]string{
	"reset":  "\033[0m",
	"red":    "\033[31m",
	"green":  "\033[32m",
	"yellow": "\033[33m",
	"cyan":   "\033[36m",
	"gold":   "\033[93m",
}

func color(code, text string) string {
	return colors[code] + text + colors["reset"]
}