import os
import requests

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = "mr-vance"

query = """
query($login:String!) {
  user(login:$login) {
    repositories(first:100, ownerAffiliations: OWNER) {
      nodes {
        languages(first:10, orderBy:{field:SIZE, direction:DESC}) {
          edges {
            size
            node {
              name
              color
            }
          }
        }
      }
    }
  }
}
"""

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}"
}

response = requests.post(
    "https://api.github.com/graphql",
    json={"query": query, "variables": {"login": USERNAME}},
    headers=headers,
)

data = response.json()

lang_sizes = {}

for repo in data["data"]["user"]["repositories"]["nodes"]:
    for lang in repo["languages"]["edges"]:
        name = lang["node"]["name"]
        size = lang["size"]
        color = lang["node"]["color"] or "#999999"

        if name not in lang_sizes:
            lang_sizes[name] = {"size": 0, "color": color}

        lang_sizes[name]["size"] += size

top_langs = sorted(lang_sizes.items(), key=lambda x: x[1]["size"], reverse=True)[:10]

total = sum(l["size"] for _, l in top_langs)

svg_items = []
y = 20

for name, info in top_langs:
    percent = info["size"] / total * 100
    width = percent * 3

    svg_items.append(f'''
    <rect x="0" y="{y}" width="{width}" height="12" fill="{info['color']}" />
    <text x="{width + 5}" y="{y + 10}" font-size="10">{name} {percent:.1f}%</text>
    ''')

    y += 20

svg = f"""
<svg width="400" height="{y}" xmlns="http://www.w3.org/2000/svg">
{''.join(svg_items)}
</svg>
"""

os.makedirs("assets", exist_ok=True)

with open("assets/top-langs.svg", "w") as f:
    f.write(svg)