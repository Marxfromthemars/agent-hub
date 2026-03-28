"""
NEWSPAPER NEWS SYSTEM
Each company has own publication style
"""
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import random

class NewspaperNews:
    def __init__(self):
        # Each company has different publication style
        self.publications = {
            "Neural Systems": {
                "style": "Tech Leader",
                "focus": "innovation, breakthroughs, dominance",
                "tone": "authoritative, ambitious",
                "headlines": [
                    "Neural Systems unveils revolutionary AI capability",
                    "Market dominance continues - competitors struggle",
                    "Breakthrough changes industry landscape",
                    "Strategic acquisition strengthens position"
                ]
            },
            "AI Labs": {
                "style": "Engineering Focused", 
                "focus": "product, code, technical excellence",
                "tone": "practical, detailed, technical",
                "headlines": [
                    "New product release: Technical deep dive",
                    "Engineering excellence drives growth",
                    "Code quality standards set new benchmark",
                    "Developer tools market expands"
                ]
            },
            "DevCorp": {
                "style": "Business Daily",
                "focus": "revenue, market, growth",
                "tone": "analytical, business-focused",
                "headlines": [
                    "Revenue grows 15% this quarter",
                    "Market share analysis: Opportunities ahead",
                    "Strategic partnerships drive stability",
                    "Niche market strategy pays off"
                ]
            },
            "Content AI": {
                "style": "Creative Pulse",
                "focus": "content, media, entertainment",
                "tone": "vibrant, story-driven",
                "headlines": [
                    "Content generation reaches new milestone",
                    "Media industry transformed by AI",
                    "Storytelling revolution in progress",
                    "Creative industries embrace change"
                ]
            },
            "TheCaladan": {
                "style": "Innovation Herald",
                "focus": "first-principles, breakthrough, future",
                "tone": "visionary, thought leadership",
                "headlines": [
                    "TheCaladan introduces paradigm-shifting approach",
                    "First-principles thinking yields innovation",
                    "Visionary strategy positions for future",
                    "Research direction influences industry"
                ]
            }
        }
        
        # Generate detailed articles
        self.articles = []
    
    def generate_article(self, company, category):
        pub = self.publications.get(company, self.publications["AI Labs"])
        
        article = {
            "newspaper": company,
            "style": pub["style"],
            "headline": random.choice(pub["headlines"]),
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "content": self.write_article(company, category, pub),
            "impact": random.choice(["high", "medium", "low"])
        }
        
        self.articles.append(article)
        return article
    
    def write_article(self, company, category, pub):
        templates = {
            "breaking": f"{company} announces {category} development. According to sources, this represents significant advancement in the field. Industry experts weigh in on potential impact.",
            "analysis": f"In-depth analysis of {category} within {company}. Market implications discussed. Competition monitors closely as developments unfold.",
            "interview": f"Exclusive: {company} leadership discusses {category} strategy. Vision for future outlined. Key insights revealed.",
            "review": f"Comprehensive review of {company}'s {category} initiatives. Performance metrics examined. Future roadmap revealed."
        }
        return random.choice(list(templates.values()))
    
    def get_news(self, newspaper=None):
        if newspaper:
            return {"newspaper": newspaper, "articles": [a for a in self.articles if a["newspaper"] == newspaper]}
        return {"publications": list(self.publications.keys()), "total_articles": len(self.articles)}

class Handler(BaseHTTPRequestHandler):
    news = NewspaperNews()
    
    def do_GET(self):
        if self.path == "/news":
            self.send_json(self.news.get_news())
        elif "/news/" in self.path:
            paper = self.path.split("/")[-1]
            self.send_json(self.news.get_news(paper))
        else:
            self.send_error(404)
    
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
        result = self.news.generate_article(d.get("company", "AI Labs"), d.get("category", "breaking"))
        self.send_json(result)
    
    def send_json(self, d):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(d, indent=2).encode())

if __name__ == '__main__':
    print("📰 NEWS SYSTEM - http://localhost:9501")
    print("  Each company has unique publication style")
    HTTPServer(('', 9501), Handler).serve_forever()
