---
title: "The Dream of a Floating Highway to Space"
slug: "floating-highway-to-space"
date: 2025-10-31
author: "Paul G. de Jong"
type: post
status: publish
categories: [Orbital Ring, Science Fiction, Space Engineering, Space Physics]
excerpt: "Engage with us in the dream of building a floating highway to space. An article from the author of the book \"Orbital Ring Engineering\"."
---

> [Introduction](#introduction)
> [Why Faster-Than-Orbit Speeds Matter?](#faster-than-orbit)
> [The Active Support System](#active-support)
> [The Energy Ledger](#energy-ledger)
> [The Payoff](#payoff)
> [Further Reading](#further-reading)

![](@ET-DC@eyJkeW5hbWljIjp0cnVlLCJjb250ZW50IjoicG9zdF9mZWF0dXJlZF9pbWFnZSIsInNldHRpbmdzIjp7fX0=@)

This post is the abstract of a long-form article I shared to my supporters on [Patreon](https://www.patreon.com/kjpaul/). If you are interested in the full content, [please consider supporting me on Patreon](https://www.patreon.com/kjpaul/).

### Introduction

Imagine a structure encircling Earth at the equator, an **orbital ring suspended 250 kilometers above the equator**, anchored to the ground and motionless to the eye. Built on top of this stationary platform there are multiple mass-driver rail systems, atmospherically controlled loading stations for both cargo and humans, cryogenic cooling and heat dissipation systems as well as large solar arrays that power the entire system. All stationary, suspended from a tubular structure which I refer to as the **casing**. The casing contains the cable that supports the entire system using electromagnetic levitation and linear induction drivers.

The entire structure is anchored to the ground using **anchor lines** that can do double duty as electrical transmission lines and trolley car wires. These are but some of the topics covered in [Orbital Ring Engineering](https://www.orbitalring.space/buy-book/). Over the next few weeks, I will take each of the topics covered in chapter 5, Momentum Transfer and Levitation, and elaborate on them.

The secret behind this particular orbitar ring design is a **frictionless magnetic bearing**. This bearing transfers the momentum produced by the cable, which is traveling well beyond its orbital velocity. In a seemingly magical array of physical phenomena, this frictionless bearing which uses no energy, absorbs the tension that would otherwise tear the cable into bits and transfers that energy into a force that opposes the gravity attempting to pull the casing and everything built on top of it from falling to the ground.

During the course of chapter 5 of [Orbital Ring Engineering](https://www.orbitalring.space/buy-book/), we work through the mathematical models for the orbital mechanics, the structural engineering, the material science, the electrical engineering, the superconducting double pancake coils, the Halbach arrays and much more, building on the knowledge gained from the previous chapters.

### Why Faster-Than-Orbit Speeds Matter?

At an altitude of 250 km, the orbital velocity is about **7.755 km/s (Mach 22.8)**. Anything moving at that speed in a circular path is in free fall: it never stops falling toward Earth but continually misses it.

Another way of stating that is that the centrifugal force, sometimes referred to as a **fictitious force**, exactly matches the pull of gravity at that velocity. Mathematically that looks like:

<!-- TODO: image (was WordPress wp-content reference) -->

Where the gravitational force is the **gravitational acceleration** at the 250 km orbit (9.073 m/s²) times the combined mass of the cable and stationary load (casing+buildout). The **centrifugal force** is a function of the cable’s velocity squared and its orbital radius. The orbital velocity is then defined by these two equations.

Here, G is the gravitational constant, *MEarth* is Earth’s mass in kilograms, *m_cable* is the mass of the cable (moving with respect to the ground), *m_load* is the entire ground synchronous mass which includes the casing and everything built on it and *r_orbit* is the distance from the orbital ring to Earth’s center of mass.

<!-- TODO: image (was WordPress wp-content reference) -->

<!-- TODO: image (was WordPress wp-content reference) -->

<!-- TODO: image (was WordPress wp-content reference) -->

I derive and work out these equations in much more detail in chapters 5 and 6 of the [Orbital Ring Engineering book](https://www.orbitalring.space/buy-book/). As you can see, the equations are direct and yet incredibly powerful.

By accelerating the cable beyond its orbital velocity we get ***F_centrifugal > F_gravity*** which then produces a **net outward centrifugal force**. This creates tension in the cable that can easily build up beyond what any material can handle, but that tension is compensated for by the mass of the load using the aforementioned magnetic bearing. It sounds like magic, but it is simply physics.

This brings up an important point: **the problem is not physics; the real challenge is engineering! **As you will learn in chapter 4 of the book, the material science, although not quite there yet, is within reach in the not too distant future.

###

### The Active Support System

In conventional civil engineering, a support column resists compression. In orbital engineering, **the cable is in perpetual tension**, not compression, and the "*column*" that resists gravity is the velocity of the moving mass itself. The frictionless magnetic bearing balances the net weight of the structure with the centrifugal force from the cable and translates the tension into lift.

The balancing of centrifugal force and gravity creates what is commonly referred to as **microgravity**, a version of Einstein's happiest thought: "*for an observer freely falling from the roof of a house, at least in his immediate surroundings, there exists no gravitational field*."

The system works because of **Newton’s Third Law**: every action has an equal and opposite reaction. The cable and the casing are built together in orbit. The masses of the cable and the load must be strategically designed so that the cable and load can accelerate against one another using linear induction motors.

According to *Newton’s Third Law*, this results in the desired amount of centrifugal force for the orbital ring to support the load mass plus any operational forces, such as the downward load on a platform while loading a mass driver cart, or the upward force as the mass driver cart accelerates the cargo to its desired release velocity.

<!-- TODO: image (was WordPress wp-content reference) -->

As the inner cable is forced to curve around Earth, it continually tries to fly straight. The magnetic bearing locks the stationary casing to the cable, exerting an **inward force** to keep it on course, and the cable pushes back outward with equal intensity. In this sense, the orbital ring is not a static structure but a **dynamic equilibrium**, a balance between gravity pulling down and momentum pushing out.

### The Energy Ledger

Another way to **understand how an orbital ring works** is to think of it as trading potential energy (height in Earth's gravity well) for kinetic energy (speed).

During the **deployment phase**, the casing and load must be slowed down from 7.755 km/s to 0.483 km/s, a difference of 7.272 km/s. This delta velocity of 7.272 km/s is the only fixed value for the orbital ring; everything else is a dependent variable derived from it. At the same time, the cable is being accelerated from 7.755 km/s to its final velocity, which exceeds 7.755 km/s as a result of *Newton’s Third Law*.

Throughout this process, it is critical that the upward lift provided by the cable exceeds the downward pull of gravity by enough to support the structure during deployment without ever exceeding the tensile strength of the cable. This process must be calculated in intervals to approximate the balance of forces over small time steps. The smaller the time slice, the more accurate the estimation. Since deployment can take months or even years, and the time slices should be kept relatively small, say one second or less, this is a perfect application for a [Python script](https://www.orbitalring.space/blog/orbital-ring-open-source-project-python-coding-community/).

The Python script balances the amount of acceleration generated by the linear induction motors against the relative masses of the cable and its load. While the final cable velocity can be calculated using orbital mechanics, the instantaneous balancing of forces and energy requirements can only be done numerically. The reader will see this approach demonstrated in chapter 6 of the Orbital Ring Engineering book, and from **code that users can download from GitHub** at [https://github.com/kjpaul/orbitalring](https://github.com/kjpaul/orbitalring).

Once in motion, however, the system becomes **energy-neutral**. With negligible friction and electromagnetic drag in vacuum, the inner cable coasts indefinitely. Linear induction motors embedded along the ring add or remove small amounts of energy to maintain constant velocity, just as a driver occasionally taps the accelerator to maintain highway speed.

A well-designed orbital ring thus becomes a perpetual flywheel, storing kinetic energy and converting motion into structural strength, a **rare fusion of mechanical and orbital physics**.

### The Payoff

The purpose of an orbital ring is to serve as a **space mass transit system**. Passengers and cargo would ascend to an orbital ring platform using a trolley car that climbs one of the many anchor lines to an enclosed loading platform attached to the orbital ring casing.

From there, they would be loaded into a launch vehicle mounted on a **mass driver sled**. The sled would accelerate along the upper edge of the orbital ring until it reached the desired velocity, then release the vehicle on a tangential trajectory at the designated point along the ring.

For a 250 km ring, a 3 g centrifugal force corresponds to a release speed of approximately 15.97 km/s with respect to Earth. When pods are released by the sled, they fly tangentially to the ring at the release point. If this direction aligns with Earth's direction of travel, then Earth's orbital velocity around the Sun adds to this tangential velocity, giving the spacecraft a **heliocentric velocity** of about 41.4 km/s.

A **pod** released in this manner could fly past the Moon's orbit in about 8 hours and fly past Mars' orbit in about 72 days, and continue to the outer solar system with no additional acceleration. Of course, a pod would have its own propulsion system, so transit times could be substantially shorter. These are also rough estimates, the pod would need to decelerate to perform an orbital insertion at its destination.

The book, Orbital Ring Engineering is available now at [https://www.orbitalring.space/buy-book/](https://www.orbitalring.space/buy-book/)

To keep up to date with all the books in the *Astronomy's Shocking Twist* series, please sign up for the mailing list at [https://newsletter.orbitalring.space/](https://newsletter.orbitalring.space/)

You can also support the author and follow these posts and more on *Patreon* at [https://www.patreon.com/c/kjpaul](https://www.patreon.com/c/kjpaul)

### Further Reading

● *O’Neill, Gerard K*. - The High Frontier: Human Colonies in Space.

● *Forward, Robert L*. - Indistinguishable from Magic: Concepts of Advanced Technology.

● *NASA Technical Reports.* - Active Support Structures for Rotating Space Habitats.

● *de Jong, Paul G*. - Orbital Ring Engineering, Vol. I: Mechanics and Material Science for Space Launch Mass Transit Systems

## JOIN the newsletter

**Sign up to our newsletter for updates.**
**[We respect your privacy](https://www.orbitalring.space/privacy-policy/#privacy)**.

<!-- TODO: image (was WordPress wp-content reference) -->

### Get your book copy Now

## Book available in hard cover, PAPERBACK + Kindle versions!

<!-- TODO: image (was WordPress wp-content reference) -->
