"""
Build Microsoft Teams App Package (manifest.json, color.png, outline.png -> DeccanAgent.zip)
"""
import json
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw

def create_color_icon(output_path: Path):
    """Create 192x192 color PNG for Teams"""
    size = (192, 192)
    img = Image.new("RGBA", size, (99, 102, 241, 255))  # Indigo background
    draw = ImageDraw.Draw(img)
    # Draw an inner circular badge
    draw.ellipse([(24, 24), (168, 168)], fill=(30, 27, 75, 255), outline=(165, 180, 252, 255), width=4)
    # Draw a stylized "D" or robot mark
    draw.rectangle([(64, 56), (84, 136)], fill=(255, 255, 255, 255))
    draw.pieslice([(56, 56), (136, 136)], -90, 90, fill=(255, 255, 255, 255))
    draw.pieslice([(76, 76), (116, 116)], -90, 90, fill=(30, 27, 75, 255))
    img.save(output_path, "PNG")

def create_outline_icon(output_path: Path):
    """Create 32x32 transparent monochrome outline PNG for Teams"""
    size = (32, 32)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Draw outline robot/letter
    draw.rectangle([(6, 6), (26, 26)], outline=(255, 255, 255, 255), width=2)
    draw.point([(11, 13), (21, 13)], fill=(255, 255, 255, 255))
    draw.line([(10, 20), (22, 20)], fill=(255, 255, 255, 255), width=2)
    img.save(output_path, "PNG")

def create_manifest(output_path: Path, app_id: str):
    manifest = {
        "$schema": "https://developer.microsoft.com/en-us/json-schemas/teams/v1.16/MicrosoftTeams.schema.json",
        "manifestVersion": "1.16",
        "version": "1.0.0",
        "id": app_id,
        "packageName": "com.deccanagent.bot",
        "developer": {
            "name": "Deccan Agents",
            "websiteUrl": "https://github.com/oxidebits/Deccan-Agents",
            "privacyUrl": "https://github.com/oxidebits/Deccan-Agents/blob/main/README.md",
            "termsOfUseUrl": "https://github.com/oxidebits/Deccan-Agents/blob/main/README.md"
        },
        "icons": {
            "color": "color.png",
            "outline": "outline.png"
        },
        "name": {
            "short": "DeccanAgent",
            "full": "Deccan Agent - Autonomous AI Coworker"
        },
        "description": {
            "short": "Autonomous AI Coworker for Jira, GitHub, and Teams",
            "full": "Deccan Agent serves as an on-call stand-in developer and Agile PM directly in Microsoft Teams."
        },
        "accentColor": "#6366F1",
        "bots": [
            {
                "botId": app_id,
                "scopes": ["personal", "team", "groupchat"],
                "supportsFiles": False,
                "isNotificationOnly": False
            }
        ],
        "permissions": ["identity", "messageTeamMembers"],
        "validDomains": ["*.ngrok-free.app", "*.ngrok.io", "*.loca.lt"]
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

def build_package():
    dist_dir = Path("teams_package")
    dist_dir.mkdir(exist_ok=True)
    
    app_id = "083bda2b-6397-47e8-9ce1-ebf1be5c313f"
    
    color_icon = dist_dir / "color.png"
    outline_icon = dist_dir / "outline.png"
    manifest_file = dist_dir / "manifest.json"
    zip_output = dist_dir / "DeccanAgent.zip"
    
    create_color_icon(color_icon)
    create_outline_icon(outline_icon)
    create_manifest(manifest_file, app_id)
    
    with zipfile.ZipFile(zip_output, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(manifest_file, "manifest.json")
        z.write(color_icon, "color.png")
        z.write(outline_icon, "outline.png")
        
    print(f"Successfully generated Teams App Package: {zip_output.resolve()}")

if __name__ == "__main__":
    build_package()
