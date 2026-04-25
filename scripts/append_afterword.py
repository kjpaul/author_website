#!/usr/bin/env python3
"""One-off: append the afterword section to ast-t1-vol-1.json if missing."""
import json
import sys
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "data" / "references" / "ast-t1-vol-1.json"

AFTERWORD = {
    "number": "afterword",
    "title": "While I Was Writing This Book",
    "references": [
        {"num": 1, "text": "NASA Ignition announcement, March 24, 2026. \\$20 billion lunar base plan, Gateway paused, Artemis III restructured to LEO demo, Artemis IV first crewed landing 2028, Space Reactor-1 Freedom nuclear Mars spacecraft launch before end 2028. See: NASA, \"NASA Unveils Initiatives to Achieve America's National Space Policy,\" March 24, 2026, https://www.nasa.gov/news-release/nasa-unveils-initiatives-to-achieve-americas-national-space-policy/. See also: Al Jazeera, \"NASA to spend \\$20bn on moon base, nuclear-powered Mars spacecraft,\" March 24, 2026."},
        {"num": 2, "text": "SpaceX lunar mass driver concept. Musk described electromagnetic launch system for lunar surface during xAI all-hands meeting, February 2026. Conceptual phase, 15-20 year estimated timeline to operational capability. See: Interesting Engineering, \"Elon Musk teases 'cannon-like' mass drivers for launches from moon,\" February 2026."},
        {"num": 3, "text": "China electromagnetic launch developments. NUDT maglev record: 1-tonne vehicle to 700 km/h in 2 seconds on 400-meter track, December 2025. See: CGTN, \"China sets world record in maglev tech with 700 km/h in 2 seconds,\" December 25, 2025. Galactic Energy electromagnetic launch pad targeting 2028 first tests. See: Orbital Today, \"China Plans Maglev Rocket Launch System by 2028,\" October 14, 2025."},
        {"num": 4, "text": "SpinLaunch pivot. \\$30M Series C funding August 2025, redirected toward Meridian Space LEO broadband constellation rather than kinetic launch system. See: Business Wire, \"SpinLaunch Announces Closing of \\$30M in Funding to Accelerate the Development of the Meridian Space Constellation,\" August 18, 2025."},
        {"num": 5, "text": "Suarez, Daniel. Critical Mass. Dutton, 2023. Second book in the Delta-v series. Features mass driver construction from in-situ asteroid materials. Winner, 2024 Prometheus Award for Best Novel. See: NSS Book Review, \"Critical Mass,\" https://nss.org/book-review-critical-mass/."},
        {"num": 6, "text": "China cable-catch booster recovery. CALT developed 25,000-tonne recovery vessel Ling Hang Zhe (Pathfinder), delivered December 2025. Arresting cable system with hooks on booster interstage, similar in principle to aircraft carrier arresting wires. Long March 10B first test flight targeting April 2026. See: Prototyping China, \"China Builds Rocket-Catching Ship,\" March 10, 2026. See also: Space.com, \"China plans to catch reusable rockets with constricting wires,\" 2025. Academic basis: \"Arresting-Cable System for Robust Terminal Landing of Reusable Rockets,\" Journal of Spacecraft and Rockets."},
        {"num": 7, "text": "Starship Flight 12 status. Block 3 vehicle (Booster 19 with Raptor 3 engines, Ship 39), first flight from second pad at Starbase. FCC approval April-October 2026. 11 prior flight tests with 3 successful booster catches. See: NASASpaceFlight.com, Starship development tracker, March 2026."},
        {"num": 8, "text": "2025 launch statistics. 324 orbital launch attempts globally, China 92, Rocket Lab Electron 21 consecutive successes, Ariane 6 four flights. See: Space Launch Report, 2025 year-end summary. Rocket Lab Neutron targeting late 2026 first flight."},
        {"num": 9, "text": "DRACO cancellation. DARPA terminated the Demonstration Rocket for Agile Cislunar Operations program, June 2025. Cited decreasing launch costs and revised cost-benefit analysis. See: SpaceNews, \"DARPA says decreasing launch costs, new analysis led it to cancel DRACO nuclear propulsion project,\" June 2025. See also: Breaking Defense, \"DARPA's DRACO nuclear propulsion project ROARs no more,\" June 2025."},
        {"num": 10, "text": "NASA/DOE lunar fission surface power. Memorandum of understanding for 100 kWe reactor, target deployment 2030. See: NASA, \"NASA, Department of Energy to Develop Lunar Surface Reactor by 2030,\" https://www.nasa.gov/news-release/nasa-department-of-energy-to-develop-lunar-surface-reactor-by-2030/."},
        {"num": 11, "text": "Russia-China lunar reactor agreement signed May 2025, targeting 2033-2035 deployment as part of ILRS. See: Space.com, \"Russia and China announce plan to build shared nuclear reactor on the moon by 2035,\" 2025. Rolls-Royce lunar reactor stalled February 2026. See: Bloomberg, \"Rolls-Royce Moon Nuclear Reactor Plan Stalls,\" February 1, 2026."},
        {"num": 12, "text": "Vera C. Rubin Observatory. First light and initial scientific alerts, February 2026. 800,000 alerts in first night of operations. Full LSST survey: entire visible southern sky every three nights, ~20 TB/night, 10-year duration. See: Rubin Observatory, \"Ever-changing Universe Revealed in First Imagery From Vera C. Rubin Observatory,\" https://rubinobservatory.org/news/first-imagery-rubin."},
        {"num": 13, "text": "NASA NIAC program. Rebooted 2011 after earlier cancellation. 2025 Phase I: 15 awards at \\$175,000 each (\\$2.625M total). See: NASA, \"NASA Awards 2025 Innovative Technology Concept Studies,\" https://www.nasa.gov/news-release/nasa-awards-2025-innovative-technology-concept-studies/."},
        {"num": 14, "text": "Edwards, B.C., \"The Space Elevator: A Revolutionary Earth-to-Space Transportation System,\" NIAC Phase I (2000) and Phase II Final Report (2003). Available at: https://www.niac.usra.edu/files/studies/final_report/521Edwards.pdf."},
        {"num": 15, "text": "Birch, P., \"Orbital Ring Systems and Jacob's Ladders,\" Journal of the British Interplanetary Society, 35, 475-497, 1982. Meulenberg, A., orbital ring studies 2008-2011, NIAC-adjacent work on LEO ring concepts for transport and space solar power."},
        {"num": 16, "text": "Goddard, Bob. Mother Moon. 2016. First book in a series set at Armstrong Base lunar colony in 2087. Goddard has lectured on Moon colonies at the National University of Science and Technology in Moscow."},
        {"num": 17, "text": "Zubrin, R., The Case for Mars, Free Press, 1996 (updated editions). Mars Direct architecture using in-situ propellant production. Foundational text for Mars settlement engineering."},
        {"num": 18, "text": "Northrup, Edwin F. (writing as 'Akkad Pseudoman'). Zero to Eighty: Being My Lifetime Doings, Reflections, and Inventions, Also My Journey Around the Moon. Scientific Publishing Co., 1937. Princeton physics professor and inventor (over 100 patents). Novel includes detailed calculations for an electromagnetic launcher's coils, power, and trajectory. One of the earliest serious treatments of electromagnetic launch in fiction."},
        {"num": 19, "text": "Long, Ian. How to Develop the Moon. YouTube channel: Anthrofuturism (@anthrofuturism). Covers economics, engineering, and philosophy of lunar development. https://linktr.ee/ianlong."},
        {"num": 20, "text": "Cain, Fraser. Universe Today (https://www.universetoday.com), founded 1999. YouTube: @frasercain. Astronomy Cast podcast with Dr. Pamela Gay, over 1,500 episodes. One of the longest-running and most reliable independent space news sources."},
        {"num": 21, "text": "International Space Elevator Consortium (ISEC). 501(c)(3) nonprofit, NSS affiliate since 2013. Annual conferences at Seattle Museum of Flight. 2026 conference: virtual, September 12-13. See: https://www.isec.org/."},
        {"num": 22, "text": "Japan Space Elevator Association (JSEA). Runs annual SPEC (Space Elevator Challenge) competition. First international space elevator competition near Mt. Fuji. See: https://www.jsea.jp/."},
        {"num": 23, "text": "National Space Society (NSS). ISDC 2025: Orlando, FL, June 19-22, 2025. See: https://isdc.nss.org/."},
        {"num": 24, "text": "The Planetary Society. Founded 1980 by Carl Sagan, Bruce Murray, Louis Friedman. Online community grown to ~20,000 members. D.C. office opened for policy advocacy. See: https://www.planetary.org/."},
        {"num": 25, "text": "British Interplanetary Society (BIS). Founded 1933. Oldest space advocacy organization. Arthur C. Clarke: member at 16, chairman 1947-50 and 1953, proposed communications satellites in 1945 BIS memorandum. See: https://www.bis-space.com/."},
        {"num": 26, "text": "Mars Society. Founded by Robert Zubrin. Annual conferences in U.S. and Europe. https://www.marssociety.org/."},
    ],
}


def main():
    data = json.loads(PATH.read_text(encoding="utf-8"))
    chapters = data["chapters"]
    existing_numbers = [str(c.get("number")) for c in chapters]
    if "afterword" in existing_numbers:
        idx = existing_numbers.index("afterword")
        chapters[idx] = AFTERWORD
        action = "replaced"
    else:
        chapters.append(AFTERWORD)
        action = "appended"
    data["last_updated"] = "2026-04-25"
    PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{action} afterword. chapters now: {len(chapters)}")
    print(f"afterword refs: {len(AFTERWORD['references'])}")


if __name__ == "__main__":
    main()
