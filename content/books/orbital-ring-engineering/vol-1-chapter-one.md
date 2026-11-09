---
title: "Chapter 1: The Ring and Its Orbit"
slug: vol-1-chapter-one
book: ast-t1
volume: 1
group_label: Technical works
group_url: /series/technical/
book_title: "Orbital Ring Engineering, Volume I: Space Mass Transit Complete Design Review"
book_short: "Volume I"
book_url: /series/technical/orbital-rings/vol-1/
references_url: /series/technical/orbital-rings/vol-1/references/#ch-01
crumb: "Chapter 1"
eyebrow: "Orbital Ring Engineering, Volume I &middot; Chapter 1 of 19"
deck: "The opening chapter of <em>Orbital Ring Engineering, Volume I: Space Mass Transit Complete Design Review</em>, as it appears in the book. Numbered citations refer to the <a href=\"/series/technical/orbital-rings/vol-1/references/#ch-01\">Chapter 1 references</a>."
description: "Read Chapter 1 of Orbital Ring Engineering, Volume I: what an orbital ring is, the 700 km equatorial orbit, the design case, and where the idea comes from."
---
An orbital ring is a loop of fast-moving cable that holds a stationary structure above the Earth, high enough to clear the atmosphere and low enough to reach from the ground. This volume builds the ring in a 700 km equatorial circular orbit, with the cable running westward. The altitude is set by safety and not by the orbital mechanics, which is the subject of Chapter 4. The orbital parameters worked out here, which are the velocity, the gravity, the ground-synchronous speed, and the circumference, are the inputs to every chapter that follows. Table 1.1 at the end of the chapter collects them with the other values of the design case, and every later chapter refers to that table.

**The premise of this book.** Here is the basic criterion behind everything in this book: it has to actually work. There will be no candy coating and no cutting corners. It will not be easy to achieve, but it is real engineering. The timeline target is 100 to 200 years, so reasonable projections of current materials are assumed. The two biggest factors are the carbon nanotube spun yarns and the mass driver launch velocities. The CNT material needs to increase from the 14 GPa demonstrated in the laboratory today to 25 GPa in mass production. That is about 25% of its theoretical material strength, and it is the biggest assumption in this book (Chapter 3). The other significant challenge is the launch velocity. For the mass driver to be useful, it needs to reach at least 10 km/s, and the goal for cargo launches is 30 km/s (Chapter 10). These are just engineering challenges. Everything else is available today, with the caveat that it will need to be mass-produced in space or on the Moon. The last three chapters, on rings at other worlds, on mission classes and launch velocities, and on what comes next, are speculative. I welcome honest peer review of both the text and the simulation code through the coding hub and the errata pages on the book's website, pauldejong.com.

Two questions are large enough that they get their own chapters next. Chapter 2 asks whether the ring could be tilted out of the equatorial plane, and shows why an equatorial orbit is effectively mandatory. Chapter 3 sizes the cable that does the lifting.

## 1.1 What Is an Orbital Ring

An orbital ring is a continuous loop of cable that circles the Earth at an altitude well above the atmosphere but well below geosynchronous orbit. The cable moves through a stationary casing at speeds considerably faster than the local circular orbital velocity. Because the cable moves faster than it needs to for a free orbit, it generates more centrifugal force than gravity demands, and this excess centrifugal force pushes outward against the casing, holding the casing up. The casing itself is not in orbit. It moves at Earth's rotational speed, roughly 516 m/s (1,860 km/h, 1,150 mph) at 700 km altitude, which is far too slow to sustain an independent orbit. The casing hangs in place because the cable holds it up from inside.

The cable is an active structural element. It is not like a bridge, which holds its load through static forces in the material. The cable holds the casing through dynamic forces: centrifugal pressure from its continuous high-speed motion through the electromagnetic bearing system. If the cable were to stop moving, the centrifugal force would vanish, and the entire structure would fall. The cable must never stop. Everything in the ring's design flows from this fact.

The casing is levitated by the cable through an electromagnetic bearing (the electromagnetic suspension, or EMS, of Chapter 7). The bearing consists of superconducting coils in the casing and ferromagnetic plates attached to the cable, and it holds a gap of approximately 10 cm between the plates and the coils. The cable never touches the casing during normal operation. The cable's velocity is maintained by linear induction motors (LIMs, Chapter 9), whose stators are mounted in the casing. The casing is the stationary part (the stator housing), and the cable is the rotor that races through it. The LIMs also perform the initial deployment: they accelerate the cable from orbital velocity up to its operational speed while decelerating the casing from orbital velocity down to ground-synchronous speed. This deployment process, which takes about 380 days at 12 MW per LIM site (Chapter 9), is what converts a freely orbiting structure into a ground-anchored one.

Once deployed, the casing is connected to the ground by anchor lines, which are essentially very long, very strong tethers that reach from the ring altitude down to the surface. At 700 km, these anchor lines are 700 km long, which is one of the most significant engineering consequences of the altitude choice. The anchor lines attach to the casing. The casing is the structural shell that houses all of the ring's ground-synchronous equipment, so everything mounted on the ring, the mass driver, the solar panels, the cryogenic plant, the factories, the habitation modules, is bolted to the casing. The cable supports the casing through the electromagnetic bearings, and the anchor lines tie the casing to the ground. The anchor lines transmit the Earth-tracking forces needed to keep the ring's ground track fixed as the planet rotates, and serve as transportation corridors for people and cargo traveling between the surface and the casing.

![Figure 1.1: The Orbital Ring in Cross Section. Schematic cross section of the ring looking west: the square CNT cable inside the casing, ferromagnetic plates on its top and bottom faces facing the EMS coil tracks, LIM stators on both sides facing reaction plates on the cable, the mass driver track and a sled on top of the casing, the ring-mounted solar panels as wings on both sides, quarters, offices, and factories hanging below in the cable's shadow, and the anchor lines and spreader arms running down.](/images/vol-1/figures/fig01_01_ring_cross_section.svg)
*__Figure 1.1: The Orbital Ring in Cross Section.__ The ring seen looking west along it, not to scale. The cable, a square of CNT 7.39 m on a side, runs through the middle of the casing and away from the viewer at 8,847 m/s (31,800 km/h, 19,800 mph) relative to the casing. The casing holds still over the ground. The casing support tracks below the cable and the lift compensation tracks above it are superconducting EMS coils facing ferromagnetic plates on the cable across a gap of about 100 mm (Chapter 7). The LIM stators on both sides drive the cable through reaction plates (Chapter 9). The mass driver track runs along the top of the casing (Chapter 10), the ring-mounted solar panels extend as wings on both sides (Chapter 8), and the quarters, offices, and factories hang below in the shadow of the cable (Chapter 5). The anchor lines and the spreader arms run down from the casing to the ground and to the suspended solar array 100 km below (Chapters 11 and 12).*

**What is built on the ring.** The ring is the structural backbone of an entire orbital infrastructure. Virtually everything hangs below the cable, for two reasons. First, the top of the casing must remain clear for the mass driver track, which runs along the full circumference. Second, the cable itself acts as a massive shield for anything placed below it. The cable's bulk, which is 8.2 meters of carbon nanotube material, stops radiation and micrometeoroids arriving from above before they reach the equipment and habitation placed in its shadow (Chapter 5).

The ring carries the following systems, listed roughly from the top of the casing downward.

- **The mass driver.** This is the ring's primary purpose: launching payloads to orbit and beyond. The mass driver is a linear synchronous motor (LSM) track that runs along the top of the casing for the full circumference. There are two mass driver rails. The high-speed rail accelerates sleds to velocities of many kilometers per second, which requires multiple laps around the ring because the acceleration distance for a high-speed, high-mass launch can exceed the circumference. The low-speed rail handles lighter payloads and shorter acceleration runs that can be completed in a single pass or a fraction of a lap (Chapter 10).
- **Solar arrays.** Electricity runs everything on the ring. The ring carries two sets of solar panels. The first set is attached to the casing and extends outward on both sides, like wings. These panels power the LIMs during deployment, at 12 MW per LIM site (Chapter 8). The second set is the suspended solar array of Chapter 12, which is much larger and generates power for the ground. It hangs 100 km below the ring, at an altitude of 600 km, as a wide strip that is held open by spreader arms. The strip cannot be spread until the anchor lines are attached to the ground, so it cannot power the LIMs during deployment, and that is why the side-mounted panels are needed.
- **HVDC power distribution.** The power generated by the solar arrays is collected and distributed around the ring via a high-voltage direct current (HVDC) transmission system (Chapter 8).
- **The casing structure.** The casing is the structural shell that contains the electromagnetic bearings and the linear induction motor coils, houses the electronics, provides mounting points for everything else, and connects to the anchor lines. It is designed to be bottom-heavy. As much mass as possible is placed below the cable to minimize the effective casing mass that would participate in a cable-casing collision during a catastrophic failure (Chapter 4). The casing mass budget is 12,000 kg per meter of ring length, which must accommodate all the components listed here. That figure is a rough design estimate with little data behind it (Chapter 16).
- **Electromagnetic suspension (EMS) coils.** The electromagnetic suspension coils are mounted inside the casing, surrounding the cable, and their tracks run continuously around the ring. The EMS system is covered in Chapter 7.
- **Linear induction motor (LIM) stators.** The linear induction motor stators are also mounted inside the casing, surrounding the cable. The LIM sites are spaced at 500 m intervals around the circumference, giving 88,946 sites for the full ring. The LIMs are covered in Chapter 9.
- **Anchor lines.** The anchor lines connect the ring to the ground. They extend downward from attachment points on the casing, reaching the surface 700 km below. The lines are made of CNT cable (the same material as the orbital ring cable, but much smaller in cross-section) and must support their own weight plus whatever loads are being transported along them (Chapter 11).
- **Mass driver reaction lines.** Every mass driver launch fires a reaction force into the casing along the direction of acceleration. Over the operating life of a busy mass driver, this reaction load is much larger than any other along-track force the ring experiences. A second set of tethers, separate from the radial anchor lines, is provided specifically to carry this load to the ground. The reaction lines run to the surface at a forward-leaning angle relative to vertical, so that the tension in the line has a tangential along-track component that absorbs the mass driver's recoil (Chapter 11).
- **Space elevator tethers and transfer stations.** The ring can serve as the lower anchor point for space elevator tethers extending up to geosynchronous orbit and beyond. A space elevator anchored at 700 km instead of the surface starts 700 km closer to GEO and avoids the atmosphere entirely. It also skips the lowest stretch of the climb, where gravity is strongest, which greatly reduces the taper ratio and the tether mass. The preferred architecture for these tethers is the tripod configuration of Chapter 13. Its single-hemisphere geometry keeps the elevator legs and any broken-tether fragments well away from the ring's equatorial plane, so that an elevator failure cannot propagate to the ring. When integrated with the ring, the elevator is a one-way descent path: returning traffic descends, while outbound traffic uses the mass driver (Chapter 13).
- **Spaceship manufacturing facilities and industrial zones.** The ring provides a platform for orbital manufacturing. Factories built on the ring have continuous access to vacuum and to solar power, and they sit in a steady 7.918 m/s² effective gravity (about 81% of surface gravity). Raw materials are delivered up from the surface via the anchor lines or down from cislunar industry via space elevator tethers attached to the ring. These industrial facilities hang below the casing and can be quite massive: the cable's enormous tension (683 GN) means that even heavy installations produce only millimeters of local cable deflection (Chapter 3). Factories, refineries, propellant depots, and assembly facilities for interplanetary spacecraft can all be built on or suspended from the ring.
- **Ground power transmission.** The ring collects solar energy continuously in space, where there is no atmosphere, no weather, no night for the 64.3% of the ring that is in sunlight at any moment, and no seasons. Some of this energy can be transmitted to the ground via the anchor lines or via microwave power beaming, providing a source of space-based solar power for the surface (Chapter 11).
- **Ring protection systems.** The debris canopy and micrometeoroid shielding system protects the casing from impacts. The protection system is a multi-layer shield, similar in concept to the Whipple shields used on the International Space Station (ISS), that absorbs and disperses the energy of small impactors before they can penetrate the casing wall and damage the cable (Chapter 15).
- **Loading stations.** These are the interface points where cargo and passengers are loaded onto the mass driver sleds for outbound launches, transferred to and from the anchor line transport vehicles for surface-to-ring travel, and disembarked from arriving space elevator climbers returning from high orbit.
- **Trolley cars and local ring transport.** Trolley-style vehicles handle two kinds of traffic. The primary function is carrying passengers and cargo up and down the anchor lines between the surface and the ring. Once at the casing level, a separate set of vehicles handles local transport between the anchor line depot and the nearby orbital ring facilities, a factory, a habitat zone, or a mass driver loading station, on the same anchor station's local stretch of casing. The ring is not used for long-distance point-to-point travel. Local trolley travel is measured in tens to low hundreds of kilometers between an anchor depot and the facilities it serves (Chapter 11).
- **Worker domiciles and towns.** A permanently operated ring needs people on it. Worker housing, life support systems, medical facilities, recreation areas, food production (greenhouses), and the other elements of a small town must be provided. Food can move up and down the anchor lines, but greenhouses and greenery are good for people, and waste management benefits from vegetation. Moving waste up and down would not be efficient, so whatever can be dealt with on the ring should be. These habitation modules are shielded against radiation (Chapter 5). The sleeping quarters and offices are placed directly under the cable, where the cable blocks most of the radiation that arrives from above, and the shielding mass goes under the floor. The towns are kept out of the South Atlantic Anomaly sector, which covers about 30% of the ring. Chapter 5 gives the crew dose at 700 km.
- **Cryogenic systems.** The high-temperature superconducting (HTS) coils in the levitation system and potentially in the LIM stators operate at approximately 70 K. Maintaining this temperature in the space environment requires a cryogenic cooling system with radiators to reject waste heat (Chapter 14).

This list is not exhaustive. The ring is a platform, and its uses will expand over time as the orbital infrastructure matures. All of the systems that must be in place at the moment of deployment have to fit within the 12,000 kg/m casing mass budget that the cable was sized to carry. Post-deployment build-out is much more forgiving. Once the cable is at operational velocity, its hypersonic stiffness allows substantial local mass concentrations to be added on top of the deployment-era casing, as Chapter 3 shows. The 12,000 kg/m number is therefore the deployment-era target, not a hard ceiling on what can ever be added to the ring.

## 1.2 Orbit Selection

We select a 700 km equatorial circular orbit. The equatorial plane is chosen because it eliminates the Earth-tracking Coriolis force that an inclined orbit would impose on the anchor lines, simplifies the deployment sequence, and avoids the continuous eddy current heating that would result from the LIMs providing sustained lateral centering forces. The altitude of 700 km is set by the catastrophic failure safety analysis in Chapter 4. These two choices together define the orbital geometry for the rest of the book.

**The orbital parameters.** All of the orbital mechanics in this book rest on two fundamental measurements: the mass of the Earth and the rate at which it spins. Earth's angular velocity is based on a sidereal day, which is the time it takes for the Earth to complete one full rotation relative to the distant stars. For orbital mechanics, the sidereal day is the correct reference because orbits are defined relative to the stars, not the Sun.

> **Definition Box: Sidereal Day.** *The sidereal day is the time for one complete rotation of the Earth relative to the distant stars, which is 23 hours 56 minutes and 4.09 seconds. It is about 4 minutes shorter than the solar day because the Earth has moved along its orbit around the Sun during that time, so it must rotate a bit more than 360° to bring the Sun back to the same position. Every orbital-mechanics calculation in this book uses the sidereal day rather than the solar day, because the orbit is fixed relative to the stars rather than relative to the Sun.*

The sidereal day is 86,164.09 seconds, and from it we get Earth's angular velocity:

![Equation 1.1: Earth's sidereal angular velocity, computed as 2π divided by the sidereal day.](/images/vol-1/equations/eq01_01_omega_sidereal.svg)
*Equation 1.1: ω<sub>sidereal</sub> (omega) is Earth's sidereal angular velocity, 2π divided by the sidereal day t<sub>sidereal</sub> of 86,164.09 seconds. The result is 7.2921 × 10⁻⁵ rad/s. This is the rotation rate the ring's casing must match to keep its ground track fixed, because that is how fast the ground beneath it is moving. Five significant figures are enough for this book: at 700 km the fifth figure is worth 7 mm/s in the casing's speed. The geodetic standard behind GPS carries the rate to 7.292115 × 10⁻⁵ rad/s, and the astronomical reference value to fourteen figures, 7.2921151467064 × 10⁻⁵ rad/s. That one is a defined constant rather than a measurement, because the real rate wanders in the eighth figure as the tides, the winds and the core move mass about the planet. The ring does not depend on any of these digits: its anchor lines hold the casing to the ground itself, so it turns with the real day (Chapter 11).*

At 700 km altitude, the orbital radius is r = R<sub>E</sub> + 700 km = 6,378.137 + 700 = 7,078.137 km = 7,078,137 m. The circular orbital velocity at this radius, which is the speed at which a freely orbiting object would travel to maintain a stable circular orbit, is:

![Equation 1.2: The circular orbital velocity at 700 km altitude.](/images/vol-1/equations/eq01_02_vorbit_700.svg)
*Equation 1.2: v<sub>orbit</sub> is the circular orbital velocity at 700 km altitude. The result is 7,504.3 m/s. Orbits farther from Earth are slower. A satellite at 700 km takes longer to orbit than one lower down because it has farther to go, and it also moves more slowly because gravity is weaker.*

where:

- v<sub>orbit</sub> is the circular orbital velocity in m/s.
- G is the gravitational constant, 6.674 × 10⁻¹¹ m³ kg⁻¹ s⁻².
- M is the mass of the Earth in kg.
- r is the orbital radius, 7,078,137 m.

The product GM is often written as μ (mu) and is called the standard gravitational parameter. Its value for Earth is μ = 3.986004418 × 10¹⁴ m³/s², known to approximately 10 significant figures with a relative uncertainty of about 2 parts per billion. The reason μ can be measured so precisely is that satellite orbits depend directly on it: by tracking a satellite's position over time, you can determine μ from the orbit without ever needing to know G or M separately. The gravitational constant G, on the other hand, is one of the least precisely known fundamental constants in physics, measured to only about 4 significant figures despite more than 300 years of increasingly sophisticated experiments [1]. Earth's mass M is similarly limited to about 4 significant figures because M = μ/G, and the uncertainty in G dominates. Orbital mechanics is a precise science, but that precision comes from measuring μ directly, not from measuring G and M and multiplying them together.

> **Definition Box: Standard Gravitational Parameter (μ).** *μ (mu) is the product of the gravitational constant G and a body's mass M: μ = GM. For Earth, μ = 3.986004418 × 10¹⁴ m³/s². It is known to roughly 10 significant figures because it can be measured directly from satellite orbits, whereas G alone is known to only about 4 significant figures. All orbital calculations in this book use μ rather than computing GM from separate values of G and M. GPS satellites, for example, depend on precise knowledge of μ for their orbital predictions, and the centimeter-level accuracy of modern geodetic GPS would not be possible without knowing μ to parts-per-billion precision.*

The gravitational acceleration at 700 km altitude tells us how hard gravity is pulling on each kilogram of the ring structure:

![Equation 1.3: The gravitational acceleration at 700 km altitude.](/images/vol-1/equations/eq01_03_g_700.svg)
*Equation 1.3: g(r) is the gravitational acceleration at 700 km altitude. The result is 7.956 m/s², which is 81.1% of the 9.807 m/s² surface value. This is the acceleration that the cable's excess centrifugal force must overcome to support the casing.*

where:

- g(r) is the gravitational acceleration at the radius r, in m/s².
- μ (mu) is Earth's standard gravitational parameter, GM, 3.986 × 10¹⁴ m³/s² (3.986004418 × 10¹⁴ to the ten figures the geodetic standard carries; four are enough here).
- r is the orbital radius, 7,078,137 m.

At 700 km, gravity is still about four fifths of its surface value. This is a common misconception about orbital mechanics: people sometimes think astronauts are weightless because gravity is weak in space. In fact, gravity at the ISS altitude of 400 km is 8.69 m/s², which is 89% of the surface value. Astronauts are weightless not because gravity is weak but because they are in free fall, continuously falling around the Earth. The orbital ring's casing is not in free fall. It is moving at only 516 m/s, far too slow for a free orbit, so it experiences the full 7.956 m/s² of gravity as a real, downward weight that the cable must support.

The ground-synchronous velocity is the speed at which the casing must travel to stay stationary over a fixed point on the ground. It depends only on the orbital radius and the Earth's rotation rate:

![Equation 1.4: The ground-synchronous velocity at 700 km altitude.](/images/vol-1/equations/eq01_04_vgeo_700.svg)
*Equation 1.4: v<sub>geo</sub> is the ground-synchronous velocity of the casing at 700 km altitude, the orbital radius r times Earth's sidereal angular velocity ω<sub>sidereal</sub>. The result is 516.1 m/s. This is the speed the casing must maintain after deployment to stay stationary over the ground. It is much slower than the free circular orbital velocity of 7,504 m/s (27,000 km/h, 16,800 mph).*

For reference, the surface velocity of a point on Earth's equator is the equatorial radius times the same angular velocity, v<sub>equator</sub> = 6,378,137 × 7.2921 × 10⁻⁵ = 465.1 m/s. The casing at 700 km moves faster (516.1 m/s) because it is at a larger radius, but both rotate at the same angular rate ω<sub>sidereal</sub>. The anchor lines connect these two velocities: the bottom of the line moves at 465 m/s with the surface, and the top moves at 516 m/s with the casing, with the velocity varying smoothly along the length.

The net downward acceleration on the casing is the gravitational acceleration minus the tiny centrifugal acceleration from the casing's own rotation with the Earth. The casing moves slowly (516 m/s), but it is still on a circular path. That path produces a small outward centrifugal acceleration:

![Equation 1.5: The net downward acceleration at 700 km altitude.](/images/vol-1/equations/eq01_05_gnet_700.svg)
*Equation 1.5: g<sub>net</sub> is the net downward acceleration on the casing at 700 km altitude, the gravitational acceleration minus the centrifugal acceleration from the casing's rotation at ω<sub>sidereal</sub>. The centrifugal term is small (0.038 m/s²), giving g<sub>net</sub> = 7.918 m/s². This is the effective weight per unit mass that the cable must support.*

where:

- g<sub>net</sub> is the net downward acceleration on the casing in m/s².
- g(r) is the gravitational acceleration at the ring, 7.956 m/s².
- ω<sub>sidereal</sub> (omega) is Earth's sidereal angular velocity, 7.2921 × 10⁻⁵ rad/s.
- r is the orbital radius, 7,078,137 m.

The ring circumference at 700 km is C = 2πr = 2π × 7,078,137 m = 44,473 km, about 1.11 times the circumference of the Earth at the equator (40,075 km). The free-orbit period at this altitude is T<sub>orbit</sub> = C / v<sub>orbit</sub> = 44,473,000 / 7,504.3 = 5,926 s = 1.65 hours. After deployment, the cable moves faster than the free orbital velocity (8,331 m/s for the retrograde cable, 30,000 km/h or 18,600 mph, as derived in Chapter 3), so its actual circuit time is shorter: T<sub>cable</sub> = C / v<sub>cable</sub> = 44,473,000 / 8,331 = 5,338 s = 1.48 hours. The cable completes a full lap in about an hour and a half. At 500 m spacing between LIM sites, the ring has 88,946 sites around its full circumference.

Seen from the ring, the Earth blocks the Sun over an arc of 2 × 64.3°, where 64.3° is the arcsine of R<sub>E</sub>/r. So at any moment 64.3% of the ring is in sunlight. That is the value at the equinoxes, when the Sun is in the plane of the ring, and the sunlit share is a little larger at other times of year. This directly affects the solar power budget (Chapter 8).

***

## 1.3 Why This Altitude

The 700 km altitude is set by safety and not by the orbital mechanics. A catastrophic cable failure at an altitude inside the atmospheric drag region would bring the whole cable down, promptly as soot from the collision ejecta and over generations as a bombardment by the large fragments.

The minimum safe altitude is set by two tests. The prompt soot from the collision ejecta has to stay well under the nuclear winter threshold, and the released cable has to stay in orbit for centuries. The cable's perigee after release is the ring altitude less about 100 km in the worst case, because the cable moves faster than circular velocity and rises when it is set free. Together the two tests put the floor at approximately 600 km. This volume builds at 700 km, which is the floor plus 100 km. From there the lowest perigee of the released cable is 602 km, and a full-section cable fragment on that orbit stays up for about 53,000 years. The full argument is the subject of Chapter 4.

**Anchor line reach.** The latitude that an anchor line can reach grows with the altitude of the ring. At 700 km a 45° line reaches about ±6.7°. That band covers Ecuador, southern Colombia, northern Brazil, equatorial Africa from Gabon to Kenya and southern Somalia, the Maldives, Malaysia, Singapore, Indonesia, and northern Papua New Guinea. Of these, Ecuador, Colombia, and Brazil lie under the South Atlantic Anomaly sector, which as of 2026 runs from about 117°W to 2°W. Stations and factories are not placed in that sector because of the increased radiation there (Chapter 5). Stations can also be built on ocean platforms in international waters, anywhere along the 70% of the ring that is outside the sector.

**Travel time from the surface.** Other treatments of tethered climbers assume speeds of 100 to 130 km/h, which would make the 700 km trip 5 to 7 hours. The trolley cars on the anchor lines are likely to be much faster than that. The acceleration is limited by the stress that the trolley's drive and guide system puts into the line, and about 0.1 g is probably the most that should be used. At 0.1 g for the first half of the trip and 0.1 g of braking for the second half, the 700 km trip takes about 28 minutes, with a peak speed of 0.8 km/s (about 3,000 km/h, 1,850 mph). The top speed the line can support depends on how the trolley's drive and guide system interacts with the cable, which Chapter 11 takes up, so the real transit time lies somewhere between about half an hour and the 5 to 7 hours of the slow climbers. For a system designed to carry millions of passengers, this transit time directly affects throughput and the passenger experience.

**The upper limit.** Radiation sets the upper end of the buildable range. The share of the ring that is free of trapped protons shrinks as the altitude rises, from about 70% at 700 km to about half at 800 km, with the magnetic field as it is in 2026. The anomaly is growing and drifting west at about 0.3° per year, so the limit comes down with time. The full radiation environment analysis is in Chapter 5.

***

## 1.4 The Design Case

Table 1.1 is the design case for this volume. The orbital values come from the equations of Section 1.2. The others are worked out in the chapters named in the last column, and every chapter that uses one of them refers to this table.

*__Table 1.1: The Design Case.__ The values used throughout this volume, and where each one is derived.*

| Parameter | Value | Derived in. |
|:---|:---|:---|
| Ring altitude | 700 km | Chapter 4. |
| Deployment altitude | 527 km, where the ring is assembled; the cable's strain raises it 173 km to 700 km as the tension builds. The 527 km rests on the assumed 500 GPa modulus of the cable | Chapters 3 and 9. |
| Orbit | Equatorial and circular | Chapter 2. |
| Cable direction | Retrograde: the cable runs westward, the casing eastward with the ground | Chapter 3. |
| Orbital radius | 7,078,137 m | Section 1.2. |
| Circumference | 44,473 km | Section 1.2. |
| Circular orbital velocity | 7,504.3 m/s | Equation 1.2. |
| Escape velocity | 10,613 m/s | √2 times the orbital velocity. |
| Free-orbit period | 98.8 minutes (1.65 hours) | Section 1.2. |
| Gravity at the ring | 7.956 m/s², 81.1% of the surface value | Equation 1.3. |
| Net downward acceleration on the casing | 7.918 m/s² | Equation 1.5. |
| Ground-synchronous velocity of the casing | 516.1 m/s | Equation 1.4. |
| Surface velocity at the equator | 465.1 m/s | Section 1.2. |
| Sunlit share of the ring | 64.3% at the equinoxes, a little more at other times | Section 1.2. |
| Cable velocity | 8,331 m/s westward, which is 8,847 m/s relative to the casing | Chapter 3. |
| Cable circuit time | 1.48 hours | Section 1.2. |
| Cable mass | 92,883 kg/m structural, 103,569 kg/m with its hardware | Chapter 3. |
| Cable cross-section | 54.6 m², a square 7.39 m on a side | Chapter 3. |
| Cable tension | 683 GN, a stress of 12.5 GPa | Chapter 3. |
| Casing mass budget | 12,000 kg/m | Chapter 16. |
| Total ring mass | 5,140 Mt | Chapter 3. |
| Levitation gap | About 100 mm between the coils and the plates | Chapter 7. |
| LIM sites | 88,946, one every 500 m | Chapter 9. |
| Deployment | 381 days at 12 MW per LIM site, 1,067 GW in all, 19.2 EJ | Chapters 3 and 9. |
| Suspended solar array | At 600 km, 100 km below the ring, held open by spreader arms every 10 km | Chapter 12. |
| Anchor lines | Tapered CNT lines, 700 km from the casing to the ground | Chapter 11. |
| Mass driver reaction lines | One every 50 km | Chapter 11. |
| Superconductor operating temperature | About 70 K | Chapter 14. |
| Space elevator | One tether through a platform in geosynchronous orbit, carrying 25 t pods | Chapter 13. |

***

## 1.5 Where the Idea Comes From

The orbital ring did not appear out of nowhere. It belongs to a line of thought about permanent space infrastructure that runs through Nikola Tesla, Yuri Artsutanov, G. Polyakov, Anatoly Yunitsky, Paul Birch, and a few modern popularizers, and the design in this book is a direct descendant of one of them.

The earliest known proposal is Nikola Tesla's. In the 1870s, recovering from cholera, he imagined an equatorial ring that would float freely and could be arrested in its spin to allow travel at a thousand miles an hour. He described it decades later in his autobiography [2], never published the engineering, and left the support mechanism ambiguous. In 1960 Yuri Artsutanov published the modern space elevator, a cable from a geostationary satellite down to the ground, and Jerome Pearson rediscovered it in the West in 1975. Those are elevators, not rings, but they introduced the idea that the way to orbit could be fixed infrastructure rather than a vehicle carrying its own energy and reaction mass.

The step from one tether to a ring around the Earth was G. Polyakov's. His 1977 article, A Space Necklace About the Earth, which NASA translated the following year [3], described a ring moving at or near orbital velocity. At that speed the outward centrifugal force only just exceeds gravity, so the structure has almost no load-bearing capacity and no stiffness, and later analysis showed it to be unstable against in-plane disturbances without active control. In 1982 Anatoly Yunitsky proposed the General Planetary Vehicle, a ring built on the equator whose internal mass stream is accelerated until the whole structure lifts off the ground, stretching by nearly 1,900 km as it rises. It is a thought experiment about an expanding launch vehicle rather than a permanent structure.

The decisive step was Paul Birch's, in a three-part series in the Journal of the British Interplanetary Society in 1982 and 1983 [4]. Three pieces of his design carry the architecture of this book. The first is the kinetic architecture: a cable moving well above orbital velocity inside a stationary casing, with magnetic bearings across a vacuum gap passing the cable's excess outward force to the casing. The casing floats on the kinetic energy of the cable inside it. That is active support, and the excess velocity is what gives the structure the stiffness and the load capacity that Polyakov's ring lacked. The second is the anchor line, which Birch called a Jacob's Ladder. Because the casing stands still over the ground and is held up from inside, a line can be dropped from it to the surface, and it only has to be as long as the ring is high. That is what breaks the materials problem of the classical elevator, which needs a cable at least 36,000 km long. The third is the deployment: launch a thin wire, accelerate it past orbital velocity until it can lift a small load, use that load to draw up a thicker cable, and repeat, so the ring pulls itself up by its own bootstraps. Chapters 3 and 9 are the descendants of that idea.

The limit Paul Birch could not design around is the hoop stress. The stress in a spinning hoop is the density times the velocity squared, whatever the radius, and the part of it that holds the casing up is the excess over the orbital value. Adding velocity adds stress, and the two cannot be set independently. Birch's rings ran at low excess velocity over orbital with 1980s materials and could carry correspondingly little, and a steel cable holding up the casing of this book would need about fifty times the mass per meter of the carbon nanotube cable of Chapter 3. Birch's force balance is unchanged; what carbon nanotube changes is the mass ratio it produces.

Not every line followed Paul Birch. Between 2008 and 2011 Andrew Meulenberg and Timothy Poston published the LEO Archipelago [5], a staged program of equatorial rings that run at orbital velocity and hold nothing up; their transport system mounts a rotating tether on the ring and catches payloads from aircraft at its tip. The rings are a small fraction of the mass of Birch's, and the price is dynamics: compressive spars a hundred kilometers long, a pickup window of seconds, and a rendezvous between an aircraft and a falling tether tip. A momentum-exchange system moves payloads one at a time. An actively supported ring is infrastructure that also moves payloads, continuously, and that is why this book takes Birch's branch.

Paul Birch's papers sat in the journals for decades. The orbital ring came back into general technical discussion through Isaac Arthur, whose YouTube channel Science & Futurism with Isaac Arthur has run since 2014 [6]. His Upward Bound and Megastructures series compare the elevator, the skyhook, the mass driver, and the ring, champion the Birch model for its material feasibility, and popularize the idea that a ring need not follow the equator (Chapter 2 is why this one does). Nikola Tesla sketched the idea, G. Polyakov formalized it, Paul Birch published the first engineering framework, Andrew Meulenberg and Timothy Poston pursued the low-mass branch, and Isaac Arthur brought the concept to a wide audience. *Why Space*, the companion to the series, tells this history at more length and treats the ring's relatives, the skyhook, the space elevator, and the mass driver, as a family. This book attempts the next step, from proposal to design review.

***

## Chapter Summary

The orbital ring in this volume operates at 700 km altitude in an equatorial circular orbit. The altitude is set by the catastrophic failure analysis in Chapter 4, which shows that lower altitudes pose an unacceptable environmental risk. The equatorial plane is chosen because it eliminates the Earth-tracking Coriolis forces that an inclined ring would carry, which Chapter 2 works out in detail. The orbital numbers that the rest of the book builds on are collected in Table 1.1, with the other values of the design case. The cable that supports this casing load, and the numbers that follow from sizing it, are derived in Chapter 3.

---

## References

References for this chapter are at [pauldejong.com/series/technical/orbital-rings/vol-1/references/#ch-01](/series/technical/orbital-rings/vol-1/references/#ch-01).
