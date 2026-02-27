

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

PAGE LEFT INTENTIONALLY BLANK

i

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

Office of NextGen

800 Independence Ave., S.W.
Washington, DC 20591

U.S. Department
of Transportation
Federal Aviation
Administration

April 26, 2023

Dear Reader:

We are pleased to share Version 2.0 of the Urban Air Mobility (UAM)  Concept of Operations
(ConOps)  with  our  Federal  Aviation  Administration  (FAA),  National  Aeronautics  and  Space
Administration (NASA), and industry partners who have provided feedback to Version 1.0 of this
document since its release in 2020. This ConOps documents the outcomes of the joint concept
development efforts undertaken to date by the FAA NextGen Office with industry stakeholders as
well as interagency coordination.

The  UAM  ConOps  Version  2.0  is  an  iterative  progression  of  work  in  the  development  of  the
concept that will be continued to mature through ongoing government and industry stakeholder
collaboration.  Future  editions  of  the  UAM  ConOps  will  provide  a  broader  and  more
comprehensive  vision  of  our  shared  partnership  for  UAM  operations  based  on  feedback  and
continued collaboration surrounding this iteration of the UAM ConOps.

This  document  is  key  element  in  maturing  the  overall  Advanced  Air  Mobility  (AAM)  concept
aimed  at  developing  an  air  transportation  system  that  moves  people  and  cargo  between  local,
regional, intraregional, and urban locations not previously served or underserved by aviation using
innovative aircraft, technologies, infrastructure, and operations. AAM will support a wide range
of passenger, cargo, and other operations within and between urban and rural environments using
new and innovative aircraft.

Sincerely,

Paul Fontaine
Assistant Administrator for NextGen (A)
ANG-1

ii

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

PAGE LEFT INTENTIONALLY BLANK

iii

Urban Air Mobility (UAM)
Concept of Operations

Executive Summary

Version 2.0
April 26, 2023

The  Federal  Aviation  Administration  (FAA)  NextGen  Office  released  the  initial  Concept  of
Operations (ConOps) v1.0 for Urban Air Mobility (UAM) in June 2020 to describe a new, future,
operational environment. UAM is a subset of Advanced Air Mobility (AAM), an initiative by the
FAA, National Aeronautics and Space Administration (NASA), and industry. The AAM initiative
aims to develop an air transportation system that moves people and cargo between local, regional,
intraregional, and urban locations not previously served or underserved by aviation using innovative
aircraft, technologies, and operations. While AAM supports a wide range of passenger, cargo, and
other operations within and between urban and rural environments, UAM focuses on flight operations
in and around urban areas. The UAM vision is supported by the introduction of a cooperative operating
environment known  as Extensible Traffic Management  (xTM), which  complements  the  traditional
provision of Air Traffic Services (ATS) for future passenger or cargo-carrying operations/flights.

This  concept  is  not  a  policy  statement  and  is  not  a  prescriptive  statement  of  what  the  far  term
integration  will  be.  It  is  a  target  description  of  the  evolution  of  integration  from  the  near-term
Innovate 28 environment to a future of high-density urban operations. The concept focuses on a
potential longer-term target supporting exploration and validation efforts. Future versions of the
ConOps will reflect the outcomes of analyses, trials, concept maturation, and collaboration.

While many of the concept elements are similar across the future cooperative environments (e.g.,
UAM, Unmanned Aircraft Systems [UAS] Traffic Management [UTM], Upper Class E Traffic
Management  [ETM]),  this  ConOps  focuses  on  UAM.  The  envisioned  evolution  for  UAM
operations  includes  an  initial,  low-tempo  set  of  operations  that  leverage  the  current  regulatory
framework and rules (e.g., Visual Flight Rules [VFR], Instrument Flight Rules [IFR]) as a platform
for  increasing  operational  tempo,  greater  aircraft  performance,  and  higher  levels  of  autonomy.
These  are  made  possible  by  increased  information  sharing  with  operations  across  a  range  of
environments, including major metropolitan areas and the surrounding suburbs. Resulting from
stakeholder input sessions, the mature state operations will be achieved at scale through a crawl-
walk-run approach, wherein:

1.  Initial UAM operations are conducted using new aircraft types that have been certified to

fly within the current regulatory and operational environment.

2.  A  higher  frequency  (i.e.,  tempo)  of  UAM  operations  in  the  future  is  supported  through
regulatory evolution and UAM Corridors that leverage collaborative technologies and techniques.

3.  New  operational  rules  and  infrastructure  facilitate  highly  automated  cooperative  flow
management  in  defined  Cooperative  Areas  (CAs),  enabling  remotely  piloted  and
autonomous aircraft to safely operate at increased operational tempos.

This  updated  UAM  ConOps  v2.0  reflects  the  continued  maturation  of  UAM  and  incorporates
feedback received on v1.0, as well as research outcomes and additional input from government
and industry stakeholders. Its focus is on clarifying elements from the initial version and providing
additional detail in response to the feedback and input.

Language and definitions have been updated to ensure consistency across the cooperative (i.e., xTM)
operating  environments  when  applicable  and  includes  an  expanded  description  of  Cooperative
Operating Practices (COPs) (previously Community Business Rules [CBRs]). However, it does
not prescribe specific solutions, detailed operational procedures, or implementation methods except
as examples to support a fuller understanding of the elements associated with UAM operations.

iv

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

Published
Date

6/26/2020

4/26/2023

Document Change Record

Document
Version

Section
Impacted

Revisions of Particular Merit

1.0

2.0

Baseline Document

Throughout   Expanded document to provide greater detail of

selected concept elements (e.g., COPs) and relationship
of UAM within the service environments (i.e., ATS and
xTM) as well as reconcile use of terms.

1.3

1.4

Updated and expanded service environment
descriptions to include ATS and xTM.

Incorporated definitions for range of terms used across
the cooperative environments (e.g., UTM, UAM, AAM,
xTM).

3.0, 3.1,
3.2, 3.3

Amended to reflect updated terms and provide greater
detail on the use of current regulatory framework to
support initial UAM operations.

4.2

4.3.5

Addition of section focused on Cooperative Operating
Practices (COPs), which replaces Community Business
Rules (CBRs)

Updated the phrasing/language describing the federated
service network supporting UAM operations.

4.4.1, 4.4.2,
4.4.3, 4.4.4

Provided additional detail for elements of UAM
Corridors, including potential evolution over time.

5.0

6.0

Updated architecture with additional details (e.g., data
exchanges specific to UAM/PSUs, depiction of
vertiports).

Updated scenarios to reflect current content in the body
of the concept.

v

Urban Air Mobility (UAM)
Concept of Operations

Table of Contents

Version 2.0
April 26, 2023

Executive Summary ..................................................................................................................... iv

1

Introduction ........................................................................................................................... 1

1.1

1.2

Scope ............................................................................................................................... 1

Background ..................................................................................................................... 1

1.2.1  Drivers for Change ...................................................................................................... 1

1.2.2  Aircraft Evolution ........................................................................................................ 2

1.2.3  Vertiport Considerations ............................................................................................. 2

1.3

Operating Environment Perspectives .............................................................................. 2

1.3.1  Overview ..................................................................................................................... 2

1.3.2  UAM Cooperative Environment ................................................................................. 3

1.3.3  Operations in the ATS Environment ........................................................................... 4

1.4

Definitions ...................................................................................................................... 4

2  Principles and Assumptions.................................................................................................. 5

3  Evolution of UAM Operations ............................................................................................. 6

3.1

Initial UAM Operations .................................................................................................. 8

3.2  Midterm Operations ........................................................................................................ 8

3.3  Mature State Operations ................................................................................................. 9

4  UAM Operational Concept ................................................................................................. 10

4.1

4.2

4.3

Overview ....................................................................................................................... 10

Cooperative Operating Practices (COPs) ..................................................................... 11

Roles and Responsibilities ............................................................................................ 12

4.3.1  FAA ........................................................................................................................... 12

4.3.2  UAM Operator .......................................................................................................... 13

4.3.3  Pilot in Command (PIC) ............................................................................................ 13

4.3.4  Provider of Services for UAM (PSU) ....................................................................... 13

4.3.5  Federated Service Network ....................................................................................... 15

4.3.6  Supplemental Data Service Provider (SDSP) ........................................................... 15

4.3.7  UAM Vertiport .......................................................................................................... 15

4.3.8  UAS Service Supplier (USS) .................................................................................... 15

4.3.9  Other NAS Airspace Users ........................................................................................ 16

4.3.10  Public Interest Stakeholders ...................................................................................... 16

vi

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

4.4

UAM Corridors ............................................................................................................. 16

4.4.1  UAM Corridor Entry/Exit Points (CEPs) .................................................................. 18

4.4.2  Conflict Management and Separation ....................................................................... 19

4.4.3  Demand-Capacity Balancing (DCB) ......................................................................... 19

4.4.4  UAM Corridor Evolution .......................................................................................... 20

4.5  Weather and Obstacles Within the UAM Environment ............................................... 22

4.6

Constraint Information and Advisories ......................................................................... 22

5  Notional Architecture .......................................................................................................... 23

5.1

Supporting Services ...................................................................................................... 24

6  UAM Scenarios .................................................................................................................... 24

6.1

Nominal UAM Operation Completed Within a UAM Corridor ................................... 25

6.1.1  Planning Phase .......................................................................................................... 25

6.1.2

In-Flight Phases ......................................................................................................... 25

6.1.3  Post-Operations Phase ............................................................................................... 26

6.2

Nominal UAM Operation Across Service Environments ............................................. 26

6.2.1  Planning Phase .......................................................................................................... 26

6.2.2

In-Flight Phases ......................................................................................................... 27

6.2.3  Post-Operations Phase ............................................................................................... 28

7  UAM Evolution .................................................................................................................... 28

Appendix A

References ........................................................................................................ 29

Appendix B

Acronyms ......................................................................................................... 30

Appendix C

Glossary ........................................................................................................... 32

vii

Urban Air Mobility (UAM)
Concept of Operations

List of Figures

Version 2.0
April 26, 2023

Figure 1: Notional Overview of Future Complementary Service Environments ........................... 3

Figure 2: Evolution of the UAM Operational Environment ........................................................... 7

Figure 3: Notional Multiple UAM Corridors................................................................................ 18

Figure 4: Early UAM Corridor Concept ....................................................................................... 20

Figure 5: Use of a Vertical Common Passing Zone ..................................................................... 21

Figure 6: Use of Lateral Passing Zones ........................................................................................ 21

Figure 7: UAM Corridor with Multiple Tracks ............................................................................ 22

Figure 8: Notional UAM Architecture .......................................................................................... 24

List of Tables

Table 1: Acronyms ........................................................................................................................ 30

Table 2: Glossary .......................................................................................................................... 32

viii

Urban Air Mobility (UAM)
Concept of Operations

1

Introduction

1.1

Scope

Version 2.0
April 26, 2023

Urban Air Mobility (UAM) enables highly automated, cooperative, passenger or cargo-carrying
air  transportation  services  in  and  around  urban  areas.  UAM  is  a  subset  of  the  Advanced  Air
Mobility  (AAM)  concept  under  development  by  the  Federal  Aviation  Administration  (FAA),
National  Aeronautics  and  Space  Administration  (NASA),  and  industry.  As  a  subset  of  AAM,
UAM focuses on operations moving people and cargo in metropolitan and urban areas.  This
Concept  of  Operations  (ConOps)  provides  an  evolving  vision  that  will  help  facilitate  further
research  on  how  to  best  assist  UAM  operations  in  the  National  Airspace  System  (NAS)  if
demand and volume exceed current capabilities.

The goal of this ConOps is to provide a common frame of reference to support the FAA, NASA,
industry, and other stakeholder discussions and decision-making with a shared understanding of
the challenges, technologies, and their potential, as well as examples of areas of applicability to
the NAS. No solutions, specific implementation methods, or detailed operational procedures are
described in this document except for example purposes (i.e., operational scenarios). This ConOps
will be further matured and updated as the concept undergoes validation, stakeholder engagement
continues, and additional operational scenarios are developed.

As  the  follow-on  to  the  UAM  ConOps  v1.0,  this  document  reflects  the  outcome  of  additional
stakeholder  engagement,  exploration,  and  validation  activities.  It  represents  the  continued
maturation  of  the  vision  for  UAM  operations,  airspace  considerations,  and  UAM  Cooperative
Operating Practices (COPs). The ConOps v2.0 identifies the need for regulatory changes to support
operations and collaborative environments with increasing density and complexity.

Current industry projections describe initial UAM operations incorporating a Pilot in Command
(PIC) onboard the UAM aircraft with potential evolution to Remote PIC (RPIC). Consistent with
the ConOps v1.0 and industry expectations, this document describes operations with an onboard
PIC operating within the cooperative environment.

1.2

Background

Transportation  is  constantly  evolving.  Each  step  forward  yields  new  opportunities  that
fundamentally change the relationship that humankind has with distance and travel. While it may
not  significantly  reduce  surface  traffic  volume,  UAM  will  provide  an  alternative  mode  of
transportation that should reduce traffic congestion during peak times.

1.2.1  Drivers for Change

For the UAM concept to mature to operational viability, it is important to understand stakeholder
business models and operational needs, as well as their impact, for incorporation into the NAS.
The  FAA  has  collaborated  with  NASA  and  participated  in  a  series  of  additional  industry
stakeholder engagements to identify examples of desired operations and environments for UAM
aircraft.

1

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

The volume of UAM operations may increase substantially. The degree to which some, or all, of
these UAM operations will require current Air Traffic Services (ATS) is undefined. To the degree
that these operations require current ATS, the increasing number of UAM operations may soon
challenge the current capabilities of the ATS workforce resources. Solutions that extend beyond
the  current  paradigm  for  crewed  aircraft  operations  to  those  that  promote  enhanced  shared
situational  awareness  and  collaboration  among  operators  are  needed.  As  the  FAA  continues  to
mature the UAM concept, additional support systems for UAM operators may be introduced.

To the degree that these operations require current ATS, the increasing number of UAM operations
could  create  new  challenges  for  ATS  workforce  resources.  Several  industry  leaders  and
stakeholders have invested heavily in this new concept and technology with the goal of eventually
being  able  to  provide  the  public  with  personal  transportation  or  cargo  services.  Personal
transportation services may be scheduled, on demand, or part of intermodal transportation links
within major urban areas. Greater public acceptance of aircraft integrity and automation in the ride
sharing economic model will also help enable increased UAM operations.

1.2.2  Aircraft Evolution

The industry vision involves  incorporating  new  aircraft design and  system  technologies.  While
some of the new designs may resemble traditional winged aircraft, some are anticipated to include
powered  lift  and  Vertical  Takeoff  and  Landing  (VTOL)  capabilities  that  facilitate  operations
between desired locations (e.g., metropolitan commutes). Major aircraft innovations, mainly with
the advancement of Distributed Electric Propulsion (DEP) and development of Electric VTOLs
(eVTOLs), may allow for these operations to be utilized more frequently and in more locations
than are currently performed by conventional aircraft.

1.2.3  Vertiport Considerations

State  and  local  governments  are  being  encouraged  to  actively  plan  for  UAM  infrastructure  to
ensure transportation equity, market choice, and accommodation of demand for their communities.
The  vertiports  and  vertistops  should  be  sited  to  ensure  proper  room  for  growth  based  on  FAA
evaluated forecasts and be properly linked to surface transportation (when possible), especially if
the  facility  primarily  supports  cargo  operations.  Local  governments  should  also  have  zoning
protections in place to protect airspace in and around vertiports and vertistops.

Metropolitan  planning  organizations,  including  state  and  local  governments,  may  incorporate
UAM  infrastructure  planning  into  larger  transportation  and  utility  planning  efforts  to  ensure
seamless  coverage  and  capacity.  Community  engagement  and  strategic  connectivity  to  larger
transportation planning efforts is key to ensuring UAM provides maximum benefits.

1.3  Operating Environment Perspectives

1.3.1  Overview

NAS  operating  environments  include  the  airspaces,  types  of  operations,  regulations,  and
procedures necessary to support an operation. Currently, the range of NAS services provided to
airspace  users  are  characterized  at  the  highest  level  under  the  category  of  ATS.  These  include

2

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

separation  (via  Air  Traffic  Control  [ATC]),  Traffic  Flow  Management  (TFM),  advisories,  and
infrastructure  (i.e.,  Communication,  Navigation,  and  Surveillance  [CNS]).  Evolving  concepts
describe  the  introduction  of  highly  automated,  cooperative  environments  such  as  Unmanned
Aircraft  Systems  (UAS)  Traffic  Management  (UTM),  AAM/UAM,  and  Upper  Class  E  Traffic
Management (ETM) to meet future NAS needs and challenges. These concepts of operations rely
on  sharing  intent  information  across  airspace  users.  This  is  governed  by  the  current,  evolving
regulatory framework as needed to support new types of operations in defined Cooperative Areas
(CAs) within which they are conducted.

1.3.2  UAM Cooperative Environment

Recent advances in technology have enabled industry development of new and innovative aircraft
types,  offering  lower  operating  costs  and  highly  automated  functionality  that  facilitates  the
introduction  of  new  types  of  operations.  At  the  same  time,  advances  in  real-time  information
sharing and the distribution of roles and functions over federated service networks are maturing
daily.  In  response  to  these  challenges  and  opportunities,  a  highly  automated,  cooperative
environment (with defined CAs) relying on a federated service network has been envisioned and
described  through  multiple  operational  concepts  as  an  additional  aspect  of  the  future  service
environments and part of the NAS. The term Extensible Traffic Management (xTM) is used to
refer to these cooperative service environments in general and is comprised of UTM, AAM/UAM,
and ETM. UAM operations, as a subset of AAM, may sometimes be conducted in CAs generally
described as UAM Corridors. The evolution of the regulatory framework will provide the needed
guidance to allow application of the innovative concepts, technologies, and techniques to support
the  emerging  aircraft  types  and  envisioned  operations.  Figure  1  provides  a  depiction  of  the
AAM/UAM environment (outlined in red) relative to the current service delivery environment, as
well as the other future cooperative environments.

As part of the future NAS, the complementary service delivery environments (i.e., ATS and xTM)
will be evaluated as potential options to assist with scalability to meet future demand challenges
and the flexibility to seize opportunities presented by the rapid evolution across the technology
horizon (e.g., cloud computing, communications, information management).

Figure 1: Notional Overview of Future Complementary Service Environments

3

Urban Air Mobility (UAM)
Concept of Operations

1.3.3  Operations in the ATS Environment

Version 2.0
April 26, 2023

All aircraft are required to comply with the regulatory requirements of the airspace within which
they are conducting operations. A UAM operation is one executed by a UAM aircraft conducted
within an airspace volume defined for UAM cooperatively managed operations. When conducting
operations in the ATS environment, a UAM aircraft will comply with the ATS requirements of the
applicable airspace class.

UAM aircraft will need to comply with applicable ATS regulations regarding VFR and IFR while
operating  in  either  Visual  Meteorological  Conditions  (VMC)  or  Instrument  Meteorological
Conditions (IMC), like any current NAS operation. Capable aircraft (and operators) may choose
to utilize ATS operating outside of a CA or cooperative services if operating in a CA based on
whichever  is  more  operationally  advantageous  to  the  airspace  user.  Consistent  with  today＊s
operations, this choice is subject to the environment and conditions for the flight.

1.4

Definitions

Automated Flight Rules (AFRs) 每 Refers to rules, applied within UAM Corridors, which reflect
the evolution of the current regulatory regime (e.g., VFR/IFR) and take into account advancing
technologies and procedures (e.g., Vehicle-to-Vehicle [V2V] and data exchanges). Under defined
conditions, the systems/automation may be allocated the role of the ※predetermined separator§ (see
paragraphs 2.7.18每2.7.22 in [1]).

Cooperative  Area  每  An  airspace  volume  (e.g.,  UAM  Corridor)  within  which  cooperatively
managed  operations  can  occur.  ATC  ensures  separation  of  non-participating  aircraft  from  the
cooperative operations and/or CA.

Cooperative  Operating  Practices  (COPs)  每  Industry-defined,  FAA-approved  practices  that
address how operators cooperatively manage their operations within the CA (i.e., UAM Corridor),
including conflict management, equity of airspace usage, and Demand-Capacity Balancing (DCB).

Cooperative  Operation  每  A  term  used  to  describe  an  operation  making  use  of  cooperative
services  (e.g.,  separation,  flow  management)  and  is  sharing/exchanging  Operational  Intent  and
other information in compliance with applicable regulations and COPs within a CA.

Federated Service Network 每 A group of service providers sharing information within a federated
network to support operating in a common, agreed manner consistent with the approved COPs.

Fully  Integrated  Information  Environment  每  Information  environment  and  key  attributes
necessary to effectively deliver services and facilitate information exchange between stakeholders.

Service  Environment(s)  每  Refers  collectively  to  the  distinct  regulatory,  procedural,  and
supporting  automation  mechanisms  through  which  services  (e.g.,  conflict  management,  flow
management)  are  provided.  In  the  future,  the  NAS  is  envisioned  to  include  the  current  (i.e.,
traditional) ATS environment as well as incorporate a complementary, cooperative xTM services
environment.

UAM Aircraft 每 An aircraft that chooses to participate in UAM operations.

4

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

UAM  Corridor  每  A  specific  type  of  CA,  as  an  airspace  volume  within  which  cooperatively
managed  operations  can  occur.  ATC  ensures  separation  of  non-participating  aircraft  from  the
cooperative  operations  and/or  CA.  It  is  comprised  of  an  airspace  volume  defining  a  three-
dimensional  route,  possibly  divided  into  multiple  segments,  with  associated  performance
requirements.

UAM Operation 每 A specific type of cooperative operation that occurs within a UAM Corridor
and is conducted in compliance with UAM specific rules, procedures, performance requirements,
and COPs.

UAM Operator 每 The person or entity responsible for the overall management and execution of
one  or  more  UAM  operations.  The  operator  plans  operations,  shares  flight  information  (e.g.,
planning, live flight), and ensures infrastructure, equipment, and services are in place to support
safe execution of flight. Throughout this document, ※UAM operator§ is often used to describe the
roles  and  responsibilities  of  the  UAM  Code  of  Federal  Regulations  (CFR)  Title  14,  Part  135
carrier, the  RPIC/PIC,  or conflict management automation to avoid allocating prematurely and
allow for evolution of the role.

Vertiports 每 A collective term for the diverse system of public and private vertiports and vertistops.

?  Vertiport 每 An area of land or structure used or intended to be used for electric, hydrogen,
and hybrid VTOL landings and takeoffs. A vertiport can include associated buildings and
facilities.

?  Vertistop  每  A  vertistop  is  a  term  generally  used  to  describe  a  minimally  developed
vertiport for boarding and discharging  passengers and  cargo  (i.e.,  no fueling,  defueling,
maintenance, repairs, or storage of aircraft, etc.).

2

Principles and Assumptions

The  following  principles  and  assumptions  guide  the  development  of  the  UAM  operating
environment and mature the UAM concept.

?  The FAA retains regulatory authority over NAS airspace and operations.

o  UAM aircraft operate within a regulatory, operational, and technical environment

as part of the NAS.

o  Any evolution of the regulatory environment will always maintain safety of the NAS.
?  The FAA reserves the right to increase aircraft operational performance requirements to

optimize the capacity/utilization of the airspace.

?  The FAA has on-demand access to information regarding UAM operations.

?  Airspace management will be static where necessary and flexible when possible.

?  UAM operators:

o  Are responsible for the coordination, execution, and management of their operations.

5

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

o  Conduct operations in compliance with the applicable regulatory framework for the
operation, the airspace within which the operation is conducted, and the applicable
COPs.

o  Maintain  conformance  to  shared  intent  and,  via  Providers  of  Services  for  UAM

(PSUs), are made aware of the intent of other relevant operations.

o  Cannot  optimize  their  own  operations  at  the  expense  of  sub-optimizing  the

environment as a whole.

?  Cooperative traffic management is  conducted  in  compliance  with a  set  of COPs,  which
would need to be collaboratively developed by relevant stakeholders and approved by the
government.

o  DCB intervention may be required as the number of UAM operations increases.
o  As  the  operational  tempo increases  the need  for  new ATC tactical deconfliction
techniques, including the formulation of new separation standards that would rely
on enhanced aircraft performance and air traffic management system fidelity may
be utilized.

o  The  architecture  (i.e.,  technology)  for  UAM  services  needs  to  be  flexible  and
scalable.  Operators  or  third-party  service  suppliers  share  information  using
common standards and messaging protocols to ensure interoperability.

?  PSUs  may  be  utilized  by  operators  to  receive  and  exchange  information  during  UAM

operations.

3

Evolution of UAM Operations

The evolution of UAM operations is characterized by the following key indicators.

1.  Operational Tempo: Representation of the density, frequency, and complexity of UAM
operations. Tempo evolves from a small number of low-complexity operations to a high-
density, high frequency of complex operations.

2.  UAM Structure (Airspace and Procedural): The level of complexity of infrastructure

and services that support the UAM environment.

3.  UAM-Driven Regulatory Changes: Existing regulations may need to evolve to address

the needs for UAM operations＊ structure and performance.

4.  UAM COPs: COPs implement the updated regulations to establish the expectations and

interactions. See Section 4.2 for additional COP details.

5.  Aircraft  Automation  Level:  The  level  of  ※PIC§  engagement  with  the  UAM  aircraft
enabling systems. The following categories describe the evolution of aircraft automation:

?  Human-Within-the-Loop (HWTL)

o  Human is always in direct control of the automation (i.e., systems)

?  Human-on-the-Loop (HOTL)

o  Human has supervisory control of the automation (i.e., systems)

6

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

o  Human actively monitors the systems and can take full control when required

or desired

?  Human-Over-the-Loop (HOVTL)

o  Human is informed, or engaged, by the automation (i.e., systems) to take action
o  Human passively monitors the systems and is informed by automation if, and

what, action is required

o  Human  is  engaged  by  the  automation  either  for  exceptions  that  are  not

reconcilable or as part of rule set escalation

6.  Location of the PIC: The physical location of the PIC. UAM operations may evolve from
a PIC onboard the UAM aircraft to RPICs/remote operators via the advent of additional
aircraft automation technologies.

Figure 2 describes the evolution of UAM operations and its relationship with increasing level of
operational tempo and the airspace structure and procedures.

Figure 2: Evolution of the UAM Operational Environment

UAM operational evolutionary stages are described in the following subsections:

?

Initial UAM operations

?  Midterm operations

?  Mature state operations

7

Urban Air Mobility (UAM)
Concept of Operations

3.1

Initial UAM Operations

Version 2.0
April 26, 2023

Initial  UAM  operations  are  conducted  by  UAM  aircraft  leveraging  current  ATS  rules  and
regulations (e.g., VFR, IFR). Key indicators of initial UAM operations are listed below.

?  Operational Tempo: Low.

?  UAM Structure (Airspace and Procedural): No UAM unique structures or procedures
exist.  Operations  will  utilize  existing  ATS  and  routes  but  may  create  new  routes  as
necessary.

?  UAM-Driven  Regulatory  Changes:  Initial  UAM  operations  are  conducted  leveraging

current rules, regulations, and local agreements.

?  UAM COPs: There are no COPs, but operational needs may be addressed in agreements

such as Letters of Agreement (LOAs).

?  Aircraft Automation Level: Consistent with current, crewed fixed-wing and helicopter

technologies (e.g., autopilots, auto-land).

?  Location of the PIC: Onboard.

For UAM aircraft that are capable, current operations are supported by existing rules, procedures,
and designated routes. As additional operations outside of the current operational paradigms are
initiated, LOAs, routes, and other procedural changes may need to be introduced to accommodate
the additional demand and location of operations within the regulatory framework of the current
ATS system. Since industry anticipates increasing operations to scale cost effectively and meet
increased demand for services, the demand for UAM operations may eventually reach the limits
of current regulations and ATS services.

3.2  Midterm Operations

With increased tempo, UAM operations will evolve through changes to the governing regulations
augmented  by  COPs,  UAM  infrastructure,  and  automation.  The  evolution  to  a  collaborative,
information-rich, data-sharing environment may require new technologies and capabilities. UAM
operators and other stakeholders will share information with the FAA, having on-demand access
to identified operational information.

Midterm operations are supported by an environment that meets the needs of increased operational
tempo. Key indicators of midterm UAM operations are listed below.

?  Operational Tempo: The operational tempo remains low; however, it may have increased
to a point that necessitates changes in the existing regulatory framework and procedures.

?  UAM  Structure  (Airspace  and  Procedural):  UAM  aircraft  are  flying  within  UAM
Corridors.  UAM  operations  are  enabled  through  confirmed  UAM  Operational  Intent〞
operation-specific information including, but not limited to, UAM operation identification,
the intended UAM Corridor(s), aerodromes and vertiports, and key operational event times
(e.g., departure, arrival) of the UAM operation. Operations are considered UAM participants
during the period of operation that exists within the UAM Corridor cooperative environment.

8

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

ATC ensures separation of non-participating aircraft from cooperative operations and/or CAs.
Deconfliction may be allocated to the UAM operator and/or PIC akin to visual separation.

?  UAM-Driven  Regulatory  Changes:  Changes  to  ATS  regulations  and  new  UAM

regulations that enable operations within UAM Corridors.

?  UAM COPs: COPs are defined by industry to meet industry standards or FAA guidelines

when specified. COPs will require FAA approval.

?  Aircraft  Automation  Level:  PICs  may  control  the  aircraft  with  emerging  capabilities

(e.g., simplified vehicle operation).

?  Location of the PIC: Primarily onboard aircraft but complemented by the introduction of

RPIC operations (with one RPIC per operation).

The  number  and  complexity  of  operations,  along  with  aircraft  capabilities  and  equipage,  may
increase beyond that effectively supported by leveraging current rules (e.g., VFR, IFR). To support
such an increase, a UAM cooperative environment may need to be developed and implemented
with  new  or  modified  procedures,  an  updated  regulatory  framework,  and  COPs.  The  UAM
cooperative  environment  (i.e.,  UAM  Corridor)  is  a  performance-based  airspace  structure  with
defined parameters that are achievable by the participants. UAM Corridors would be known to
airspace  users  and  governed  by  a  set  of  rules  which  prescribe  access  and  operations.  Where
supporting infrastructure and support services meet participation requirements, UAM operations
may be conducted. Operators whose aircraft meet performance and participation requirements may
conduct operations within the UAM Corridor.

Initially, the number of UAM Corridors may be low or limited in use, but over time, additional
UAM Corridors may be introduced as they may be utilized in airspace areas where traffic volume
requires their establishment in the interest of safety and efficiency. The UAM Corridors may transit
any applicable airspace classes.

Operations within UAM Corridors may be supported by COPs collaboratively developed by the
stakeholder community, based on industry standards and/or FAA guidelines, and approved by the
FAA,  as appropriate,  to  ensure that  the  agency＊s regulatory  authority is  maintained (e.g., NAS
safety,  equitable  access,  security).  The  collaborative  development  of  COPs  would  allow  for
stakeholders to agree on norms of interactions, which may reduce the need for ATC tactical control
of  individual  flights  and  management  of  access.  The  collaboratively  developed,  transparent,
standard COPs augment the envisioned regulatory foundation for UAM operations.

3.3  Mature State Operations

As  the  UAM  operational  tempo  increases,  UAM  operations  may  further  evolve  to  support
operational demand. Key indicators of mature state UAM operations are listed below.

?  Operational Tempo: The operational tempo increases significantly. Higher operational

tempo needs drive the increased maturity for the other indicators.

?  UAM Structure (Airspace and Procedural): UAM operations continue to occur within
UAM Corridors. The UAM Corridors may form a network to optimize paths to support an

9

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

increasing number of vertiports; the internal structure of the UAM Corridors is expected to
increase in complexity, and the necessary performance parameters for UAM participation
may  increase.  ATC  ensures  separation  of  non-participating  aircraft  from  cooperative
operations/CAs. Deconfliction may be allocated to the UAM operator, PIC, or operator＊s
automation.

?  UAM-Driven Regulatory Changes: Extensive UAM-driven regulations will be necessary

to enable cooperative operations within UAM Corridors.

?  UAM COPs: The complexity of COPs and FAA involvement in establishing guidelines

and approving COPs may evolve to match the specific topic addressed.

?  Aircraft Automation Level: Automation improvements may lead to HOVTL capabilities.

?  Location of the PIC: Remote piloting is more widely available and as  frequent as PIC

operations.

Additional  increases  in  the  tempo  of  midterm  operations  could  require  advances  to  the  UAM
environment  and  aircraft.  To  overcome  the  constraints,  UAM  operations  may  evolve  to  UAM
mature  state  operations  through  advances  to  data  sharing,  DCB,  UAM  structure,  and  aircraft
automation. Mature  state operations may also include additional  COPs  accompanied  by UAM-
driven regulatory changes.

4

UAM Operational Concept

This section provides an overview of the UAM operational concept and COPs, followed by key
definitions and descriptions of roles and responsibilities, UAM Corridor characteristics, weather
and other obstacles within the UAM environment, and constraint information and advisories.

4.1

Overview

A UAM operator performing a UAM operation is cooperatively sharing information and engaging
cooperative services to assure the safe and efficient conduct of the flight within a UAM Corridor.
The  UAM  Corridor  structure,  UAM  procedures,  information  sharing,  and  UAM  performance
criteria enable increasing operational tempo and minimize impact to ATS. UAM operations are
supported  by  PSUs  that  comprise  a  federated  service  network  to  enhance  the  capabilities  of
individual  UAM  operators/PICs  in  all  phases  of  operations  through  exchange,  analysis,  and
mediation of information among all relevant actors (e.g., UAM operators/PICs, PSUs, the FAA,
and public interest stakeholders).

Any  aircraft  operating  within  a  UAM  Corridor  must  meet  the  performance  and  participation
requirements of the UAM environment. Within UAM Corridors, deconfliction is allocated by ATC
to UAM operators and/or PIC. The UAM community will collaboratively develop and establish
COPs as standards for operations. The FAA may contribute to COP guidelines but will approve
COPs based on the specific focus, topic, or area addressed by the COP. UAM Corridor design,
performance, and participation requirements, as well as UAM COPs, may be designed to reduce
ATC  involvement  with  UAM  off-nominal  events  by  implementing  standardized  off-nominal
protocols. UAM aircraft operating outside UAM Corridors must follow the operational rules and
procedures applicable to the corresponding airspace.

10

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

The  concept  represents  an  early  step  in  the  envisioned  evolution  of  the  regulatory  framework,
development of operating rules and performance requirements commensurate with demands of the
operation, and data exchange with information architecture to support UAM operator and FAA
responsibilities. UAM leverages a common, shared, technical environment, where the operators
are  responsible  for  coordination,  execution,  and  management  of  operations  consistent  with  the
regulatory  framework  and  applicable  COPs.  This  networked  information  exchange  is  the
cornerstone for stakeholders to plan, manage, execute, and oversee UAM operations. Additional
stakeholders can access UAM shared operational information on demand.

4.2

Cooperative Operating Practices (COPs)

Foundational  to  the  success  of  the  envisioned,  federated,  highly  automated,  cooperative
environment is the establishment of common business rules across relevant stakeholders, referred
to as COPs. Development, adoption, and implementation of COPs will require collaboration across
multiple stakeholders〞including operators, industry, and the FAA as the regulator〞to identify
and resolve a broad range of questions and challenges. Examples of these questions include ※what
rules are needed?§, ※how are they expressed?§, and ※how will they be managed?§

COPs are characterized as industry-defined, FAA-approved practices that address how operators
cooperatively  manage  their  operations  within  the  cooperative  UAM  environment,  including
conflict management, equity of airspace usage, and DCB.

They  are consistent with  and augment  updates to  the regulatory  framework.1 The development
timeframe  will  be  driven  by  the  pace  at  which  operators  desire  to  execute  cooperative  UAM
operations distinct from those conducted under the current regulatory framework (e.g., VFR, IFR).
As the tempo and complexity of UAM operations increases, it is anticipated that the complexity
and range of topics covered by COPs will also increase. The relationship between industry and
government (e.g., FAA, Department of Transportation [DOT]) differs based on the focus of the
specific COP. In some instances, the rules or topic area of an individual COP may determine the
level of engagement necessary with the regulatory authority. The level of engagement also has
implications for the level of involvement that the authority will undertake as part of the applicable
coordination  for  the  specific  COP.  The  range  of  engagement  by  the  regulator  may  span  from
minimal to high levels. At higher levels, significant documentation, and testing, as well as formal
acceptance, authorization, or qualification, may be necessary prior to operational use by industry.

Another aspect of the relationship between government and industry before a specific COP may
be used operationally is ※equity interest.§ This refers to how closely the topic/area covered by the
specific COP is related to government responsibilities (i.e., mission) or policies. Some COPs, such
as those focused on aviation safety, fall directly under the FAA＊s regulatory mission. Other COPs,
such  as  avoiding  unnecessary  anti-competitive  technical  specifications  for  participation  in  the
federated  service  network,  may  be  subject  to  policies  that  fall  under  the purview  of  regulatory
agencies beyond the FAA.

1 Significant efforts will be required to review potential rules, regulations, and guidance material that govern UAM
operations (e.g., 14 CFR Parts 135, 91, 23, 25, 27, 29) to identify any updates required to enable the implementation
and regulation of UAM operations within the NAS.

11

Urban Air Mobility (UAM)
Concept of Operations

4.3

Roles and Responsibilities

Version 2.0
April 26, 2023

This section defines the roles and responsibilities for actors associated with UAM operations.

4.3.1

FAA

The FAA performs regulatory, ATC, and NAS data exchange roles for UAM, as detailed in the
following subsections.

4.3.1.1  Regulation

The FAA is the federal  authority over aircraft operations in all airspace  and the regulatory and
oversight authority for civil operations in the NAS. The FAA maintains an operating environment
that  ensures  airspace  users  have  access  to  the  resources  needed  to  meet  specific  operational
objectives  and  that  shared  use  of  the  airspace  can  be  achieved  safely  and  equitably.  The  FAA
develops  or  modifies  regulations  to  support  UAM  operations.  The  FAA  will  approve  COPs  to
ensure that the FAA authority is maintained (e.g., NAS safety, equal access to airspace, security).
The  FAA  will  define,  maintain,  and  make  publicly  available  UAM  Corridor  definitions  (e.g.,
routes and altitudes) and manage the performance requirements of UAM Corridors.

4.3.1.2  ATC

The primary purpose of ATC is to maintain safe movement of aircraft operating within the NAS.
For high-density UAM operations, this may be accomplished through ATM modernization. ATC
will ensure the separation of non-participating aircraft from the cooperative operation and/or CAs.
As appropriate, ATC may issue traffic advisories regarding known UAM operations (e.g., active
UAM Corridors) to aircraft receiving ATC services. ATC may request information as needed from
participating  actors  and  may  receive  automated  notifications  in  accordance  with  applicable
requirements.

The ATC responsibilities that enable UAM operations are to:

1.  Set UAM Corridor availability (e.g., open or closed) based on operational design (e.g., time

of day, flow direction of a nearby airport).

2.  As appropriate, provide traffic advisories regarding known UAM operations (e.g., active

UAM Corridors) to aircraft receiving ATC services.

3.  Respond to UAM off-nominal operations as needed.

4.  When  tactical  separation  assurance  is  required,  provide  current  or  newly  developed

services appropriate to the airspace in which the UAM aircraft is operating.

To fulfill their responsibilities, ATC may review any pertinent information from UAM operations.

4.3.1.3  NAS Data Exchange

FAA NAS data sources are available to UAM operations via FAA-industry exchange protocols.
This allows for authorized data flow between the UAM community and FAA operational systems.

12

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

This interface between the FAA and UAM stakeholders is a gateway such that external entities do
not have direct access to FAA systems and data. FAA data sources available via the FAA-industry
data exchange include, but are not limited to, flight data, restrictions, charted routes, and active
Special Activity Airspaces (SAAs).

4.3.2  UAM Operator

UAM operators may conduct operations as scheduled services or on-demand services via a request
from an individual customer or intermodal operator. UAM operators are responsible for regulatory
compliance and all aspects of UAM operation execution. Use of the term ※UAM operator§ in this
document  indicates  airspace  users  electing  to  conduct  operations  via  cooperative  management
within the UAM environment.

The UAM operator obtains current conditions from PSU and Supplemental Data Service Provider
(SDSP) services (e.g., environment, situational awareness, strategic operational demand, vertiport
availability,  supplemental  data)  to  determine  the  desired  UAM  Operational  Intent  information.
This may include location of flight (e.g., vertiport locations), route (e.g., specific UAM Corridors),
UAM Corridor entry or exit point, and estimated flight time.

UAM operators must have a confirmed UAM Operational Intent to operate in UAM Corridors.
UAM Operational Intent data serves the following primary functions.

1.  Informs other UAM operators of nearby operations within the UAM Corridor to promote

safety and shared awareness

2.  Enables strategic deconfliction

3.  Enables identification and distribution of known airspace constraints and restrictions for

the intended area of operation

4.  Enables  distribution  of  spatially  and  temporally  relevant  advisories,  weather,  and

supplemental data

5.  Supports  cooperative  separation  management  services  (e.g.,  conformance  monitoring,

advisory services)

The UAM operator also plans for off-nominal events. This includes an understanding of alternative
landing sites and the airspace classes that border the UAM Corridor(s) for the operation. Upon
completion of the operation, the UAM operator notifies the PSU.

4.3.3

Pilot in Command (PIC)

The PIC is the person aboard the UAM aircraft who is ultimately responsible for the operation and
safety  during  flight.  This  ConOps  assumes  a  pilot  onboard  the  aircraft;  however,  operations
described do not preclude a remote pilot or automated operations.

4.3.4

Provider of Services for UAM (PSU)

A PSU is an entity that supports UAM operators with meeting UAM operational requirements that
enable  safe,  efficient,  and  secure  use  of  the  airspace.  A  PSU  is  the  primary  service  and  data

13

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

provider for UAM stakeholders and the interface between the UAM ecosystem and the FAA. A
PSU can be a separate entity from the UAM operator, or an operator can act as its own PSU. When
confirming  the  UAM  Operational  Intent,  a  PSU  may  act  on  behalf  of  an  operator  who  has
subscribed to its offered services within the updated regulatory framework established by the FAA
for instances when an operator does not act as its own PSU.

A PSU:

1.  Provides a communication bridge between federated UAM actors, from PSU to PSU via
the network, to support its subscribing UAM operator＊s ability to meet the regulatory and
operational requirements for UAM operations.

2.  Provides its UAM operators with information gathered from the network about planned
UAM operations in a UAM Corridor so that UAM operators can ascertain the ability to
conduct safe and efficient missions.

3.  Analyzes and confirms that a submitted UAM Operational Intent is complete, consistent
with  current  advisories  and  restrictions,  and  strategically  deconflicted  considering
previously confirmed UAM Operational Intents, COPs, UAM Corridor capacity, airspace
restrictions, vertiport resource availability, and adverse environmental conditions.

4.  Provides the confirmed UAM Operational Intent to the federated service network.

5.  Distributes notifications (e.g., constraints, restrictions) for the intended area of operation.

6.  Distributes FAA operational data and advisories, weather, and supplemental data.

7.  Supports  cooperative  separation  management  services  (e.g.,  conformance  monitoring,

advisory services).

a.  Assists with coordinating UAM Corridor use status; UAM Corridor use status (e.g.,
occupied, unoccupied) is an indication that UAM operations are being conducted
or not.

8.  Archives  operational  data  in  historical  databases  for  analytics,  regulatory,  and  UAM

operator accountability purposes.

9.  Negotiates airport access through the airport＊s sponsor.

These key functions allow a PSU to support cooperative management for UAM operations without
direct FAA involvement on a per flight basis.

PSU  services  support  operations  planning,  UAM  Operational  Intent  sharing,  deconfliction,
airspace management functions, and off-nominal operations that UAM operators may encounter.
PSUs may provide value-added services to subscribers that optimize operations or provide SDSP
services  in  support  of  UAM  operations.  PSUs  exchange  information  with  other  PSUs  via  the
federated service network  to  enable  UAM  services  (e.g.,  exchange  of UAM  Operational  Intent
information, notification of UAM Corridor status, information queries). PSUs also support local
municipalities and communities as needed to gather, incorporate, and maintain information that
may be accessed by UAM operators.

14

Urban Air Mobility (UAM)
Concept of Operations

4.3.5

Federated Service Network

Version 2.0
April 26, 2023

The  federated  service  network  is  the  collection  of  connected  PSUs  that  share  subscriber
information, FAA data, supplemental data, and data from other entities (e.g., PSUs, FAA, public
interest  stakeholders)  to  provide  a  fully  integrated  information  environment  to  support  UAM
operations. Since multiple PSUs can provide services in the same geographical area, the federated
service  network  facilitates  the  availability  of  data  to  the  FAA  and  other  entities  as  required  to
ensure safe operation of the NAS and any other information sharing functions including security
and identification.

4.3.6

Supplemental Data Service Provider (SDSP)

UAM operators and PSUs use supplemental data services to access supporting data including, but
not limited to, terrain, obstacle, and specialized weather. PSUs are also able to serve as SDSPs for
subscribed UAM operators. SDSPs may be accessed via the federated service network or directly
by UAM operators.

4.3.7  UAM Vertiport

Vertiports, used as  a collective term, are  expected to be a diverse system of public and private
vertiports and vertistops. These facilities are categorized to identify the variety of aircraft they can
support based on facility design and operations. Vertiports and vertistops support passenger and
cargo operations for aircraft operating in VFR, IFR, and AFR.

UAM operators are expected to utilize whichever vertiport configuration meets their operational
needs.

A vertiport is a designated area that meets the capability requirements to support UAM departure
and  arrival  operations.  The  UAM  vertiport  provides  current  and  future  resource  availability
information for UAM operations (e.g., open/closed, pad  availability)  to  support UAM operator
planning and PSU strategic deconfliction. UAM vertiport information is accessible by the operator
via the federated service network and supplemental vertiport information may be available via the
SDSP. The vertiport information is used by UAM operators and PSUs for UAM operation planning
including  strategic  deconfliction  and  DCB;  however,  the  vertiports  do  not  provide  strategic
deconfliction or DCB services.

4.3.8  UAS Service Supplier (USS)

UAS Service Suppliers (USSs) are entities that support UAS operations under the UTM system
(see the UTM ConOps v2.0 [2] for more details). Potential scenarios may exist where USSs and
PSUs need to share information to ensure cooperative separation during UAM landing and takeoff
phases of flight within UTM environments (i.e., under 400 feet).

From a UAM operational perspective, USSs may interact with PSUs by:

1.  Enabling  UTM  operations  to  use  federated  service  network  services  to  cross  a  UAM

Corridor.

15

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

2.  Supporting  UAM  off-nominal  operations  as  needed  (e.g.,  UAM  operations  executing

emergency landings impacting UTM operation areas).

3.  Supporting UTM off-nominal operations as needed (e.g., UTM operation deviating from

filed Operational Intent near a UAM vertiport).

4.3.9  Other NAS Airspace Users

Other NAS airspace users are any non-UAM aircraft operation within the NAS. These users would
have  the  responsibility  to  know  about  and  meet  the  relevant  performance  and  participation
requirements to operate in open UAM Corridors or avoid active UAM Corridors. UAM Corridor
definitions and availability will be publicly available for these users to access.

4.3.10  Public Interest Stakeholders

Public interest stakeholders are entities declared by governing processes (e.g., COPs) to be able to
access  UAM  operational  information  and  notifications.  This  access  may  support  activities
including, but not limited to, public right to know, government regulatory, government assured
safety  and  security,  and  public  safety.  Examples  of  public  interest  stakeholders  are  local  law
enforcement and United States federal agencies.

4.4

UAM Corridors

As  described  earlier,  initial  UAM  operations  are  expected  to  make  use  of  the  flexibility  in  the
current regulatory framework (e.g., VFR, IFR) to meet their operational and mission needs. Over
time, the number of UAM operations are expected to increase, the specific areas/locations where
operators desire to conduct the operations may expand, and aircraft capabilities (e.g., equipage,
performance) could advance. Corridors may offer the opportunity to respond to what could be new
levels and types of service demands while taking advantage of the aircraft＊s capabilities without
adversely impacting current service levels.

The concept of UAM Corridors envisions safe and efficient UAM operations that may not require
traditional ATC services in certain situations, are available to any aircraft appropriately equipped
to  meet  the  performance  requirements,  and  would  be  created/implemented  when  operationally
advantageous. The UAM Corridors could help support the increasing operational tempo through
increased capabilities (e.g., aircraft performance), UAM Corridor structure, and UAM procedures.
At increased UAM traffic levels, UAM Corridors could be a mechanism for distinguishing and
keeping separate the different regulatory frameworks〞those applicable to UAM operations versus
those operating under the current (e.g., IFR, VFR) or UTM regulations.

UAM Corridors would be designed consistent with applicable environmental considerations and
may be implemented in areas where it is operationally advantageous. The UAM Corridors may
transit  all  airspace  classes.  It  is  anticipated  that  UAM  Corridors  may  exist  simultaneously  at
locations and in airspace classes with constructs (e.g., VFR flyways/corridors, IFR) leveraged for
initial UAM operations.

Operations  within  UAM  Corridors  may  have  operational  performance  and  participation  (e.g.,
UAM  Operational  Intent  sharing,  deconfliction  within  the  UAM  Corridor)  requirements.  The

16

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

performance  and  participation  requirements  for  a  UAM  Corridor  may  vary  between  UAM
Corridors.  In  addition,  performance  requirements  and  UAM  Corridor  definition  (e.g.,  volume,
location) support accommodations for most UAM off-nominal operations where the UAM aircraft
can  complete  the  operation  safely.  Any  operator  meeting  the  UAM  Corridor  performance  and
participation requirements may operate within or crossing the UAM Corridor. The crossing of a
UAM  Corridor  by  an  aircraft/operator  not  participating  in  the  cooperative  environment  (e.g.,
general aviation) remains an area of exploration as the UAM Corridor concept, specific features,
uses, and requirements mature. As UAM Corridor geometry is better understood, the foundational
elements of UAM Corridor crossings may be analyzed by stakeholders.

UAM Corridor definitions are available to  stakeholders  for  planning and operational use. ATC
will be involved in the implementation and execution of UAM Corridors for the airspace for which
ATC  is  responsible.  Other  NAS  users  will  be  aware  of  UAM  Corridors  through  airspace
familiarization associated with flight planning or ATC flight plan approval or advisories. UAM
Corridor design considerations should include:

1.  Minimal  impact  to  existing  ATS  and  UTM  operations  while  maintaining  equity  for  all

operators.

2.  Public interest stakeholder needs (e.g., local environmental and noise, safety, security).

3.  Stakeholder utility (e.g., customer need).

UAM  Corridor  availability  (e.g.,  open,  closed)  would  be  in  accordance  with  ATC  operational
design  (e.g.,  nearby  airport  configurations/change).  UAM  Corridor  availability  may  be
communicated through the federated service network to PSUs and UAM operators. In addition to
UAM  Corridor  availability  established  by  ATC,  PSUs  determine  UAM  Corridor  status  that
identifies if one or more UAM operations are occurring somewhere  within the UAM Corridor.
UAM Corridor usage information may be used by the FAA or other stakeholders for situational
awareness.

Initially, the UAM Corridors may support point-to-point UAM operations. As UAM operations
evolve, UAM Corridors may be segmented and connected to form more complex and efficient
networks of available routing between points (e.g., vertiports). Figure 3 shows a small number of
point-to-point UAM Corridors.

17

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

Figure 3: Notional Multiple UAM Corridors

4.4.1  UAM Corridor Entry/Exit Points (CEPs)

Some UAM operations may be conducted wholly within the cooperative environment. However,
most operations are anticipated to transit both service environments (i.e., ATS and xTM [UAM]).
Corridor Entry/Exit Points (CEPs) refer to the defined points in space at which an aircraft crosses
from one environment to another.

CEPs may be ※established§ in that they are defined as part of the UAM Corridor itself. An example
would be established points at either end of a UAM Corridor that are defined and disseminated as
part of the UAM Corridor definition/description. They may also be ※operation-defined,§ which are
those  points  in  space  on  the  boundary  between  the  service  environments  (i.e.,  ATS  and  xTM
[UAM]) along an accepted intent or trajectory that has not already been established.

Specific requirements or limitations regarding the use of CEPs may be addressed in  applicable
COPs  and  regulatory  framework.  Aircraft  entering  or  exiting  a  UAM  Corridor  must  meet  the
requirements of the airspace (e.g., Class B, C, D, E) they intended to use external to the UAM
Corridor.

18

Urban Air Mobility (UAM)
Concept of Operations

4.4.2  Conflict Management and Separation

Version 2.0
April 26, 2023

Conflict management across the NAS includes the strategic activity of airspace organization and
management. In certain situations, when operationally advantageous, UAM Corridors may enable
UAM  operations  without  traditional  ATC  services.  Separation  of  operations  within  UAM
Corridors  may  be  provided  through  a  layered  approach  of  strategic  and  tactical  deconfliction
methods.  Strategic  deconfliction  envisions  the  sharing  of  flight  intent  and  the  collaborative
execution of the COPs relevant to deconfliction. In later stages, capabilities relying on V2V data
exchanges  guiding  the  execution  of  aircraft  separation  may  also  mature  sufficiently  for
implementation.

When  operating  within  a  UAM  Corridor,  FAA  regulations  and  COPs  direct  the  manner  of
interactions across relevant actors for strategic and tactical deconfliction. UAM operators remain
responsible  for  the  safe  conduct  of  operations,  including  operating  relative  to  other  aircraft,
weather,  terrain,  and  hazards  and  avoiding  unsafe  conditions.  UAM  separation  is  achieved  via
shared UAM Operational Intent, shared awareness, strategic deconfliction of flight intent, and the
establishment of procedural rules.

While strategic deconfliction within UAM Corridors could occur during UAM Operational Intent
planning, the need may remain for in-flight coordination, sharing, and tactical deconfliction. Initial
analysis indicates strategic deconfliction in the planning phase may not be sufficient to support the
operational tempo described as desired by industry. In the event a UAM aircraft operates outside
of  the  bounds  of  shared  UAM  Operational  Intent,  notifications  of  the  off-nominal  event  and
updates to the UAM Operational Intent, if applicable, would be shared via the federated service
network. Initial separation in UAM Corridors may leverage applicable VFR/IFR mechanisms (e.g.,
※see-and-avoid§).  If  aircraft  technology  and  capabilities  (e.g.,  equipage)  evolve  and  mature,
separation  minima  and  AFRs  may  be  introduced  to  provide  higher  capacity  and  support  the
projected increase in demand (i.e., operational tempo). The regulatory framework governing UAM
operations would need to evolve significantly to account for the increasing levels of performance
and  automation.  The  maturation  and  implementation  of  both  the  advanced  technologies  and
updated regulatory framework are coupled to changes in the separation minima and, by extension,
the available throughput of a given UAM Corridor. The need for DCB capabilities or initiatives
will be coupled to the pace at which the operational tempo increases and the envisioned advances
in aircraft performance (e.g., equipage, capabilities) are realized.

4.4.3  Demand-Capacity Balancing (DCB)

DCB  is  applied  when  the  requested  resources  cannot  support  the  collective  UAM  Operational
Intent demand. In certain circumstances, the excessive demand may not be due to UAM Corridor
capacity  but  due  to  other  factors  such  as  congestion  at  origin  or  destination.  Initial  analysis  of
strategic  deconfliction  to  eliminate  tactical  maneuvering  identified  that  the  operational  tempo
desired by UAM operators cannot be supported solely through strategic planning/deconfliction.
The ※buffer§ necessary to account for uncertainty as the operational tempo increases leads to the
eventual need for tactical deconfliction and DCB capabilities to optimize efficiency.

Within the UAM Corridor, flow management functions, including DCB, will be provided through
Cooperative Flow Management (CFM) services. The business rules governing the execution of

19

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

CFM are included in relevant COPs, which are consistent with FAA authority including access,
equity, safety, and security.

4.4.4  UAM Corridor Evolution

Initial UAM operations, characterized by low tempo and low complexity, will be executed using
the current regulatory framework. As the tempo and complexity of operations increases, options
available  in  the  current  regulatory  framework  (e.g.,  VFR  corridors/flyways,  T-routes)  may
accommodate the growth. As the operations continue to increase in volume and complexity, the
implementation  of  simple  UAM  Corridors  may  become  operationally  advantageous  for  the
airspace  users  and/or  the  ATS  service  providers.  Initial  UAM  Corridors  are  expected  to  be
※simple§ in design (e.g., one-way UAM Corridors or single track in each direction), as illustrated
in Figure 4. As UAM Corridors become more defined, AFR will likely be available, consistent
with the evolving regulatory framework.

Figure 4: Early UAM Corridor Concept

With continued growth,  UAM  operational demand  may result in  exceeding  a  UAM Corridor＊s
initial  design  capacity,  at  which  point  increased  capacity  may  be  gained  through  additional
structure  including  tracks  and  increased  performance  capabilities  (e.g.,  ability  to  safely  reduce
separation minima  within  the UAM  Corridor through improvements in  navigation  and/or other
technologies). Additional options include variations in UAM Corridor topology to meet specific
challenges  such  as  ※passing  zones§  as  shown  in Figure  5  and  Figure  6.  Note:  An  aircraft  (and
operator)  meeting  the  performance  requirements  of  a  UAM  Corridor  as  well  as  those  of  the
surrounding  airspace  class  (i.e.,  ATS  environment)  may  elect  to  operate  in  whichever  service
environment they determine to be operationally advantageous.

20

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

Figure 5: Use of a Vertical Common Passing Zone

Figure 6: Use of Lateral Passing Zones

As the operational tempo and breadth of UAM aircraft physical performance (e.g., speed) continue
to increase, Figure 7 depicts a notional internal UAM Corridor structure comprised of multiple
※tracks.§  The  tracks  reflect  additional  internal  structure,  which  may  also  require  increased
performance  requirements  that  support  an  increased  operational  tempo  within  the  same  UAM
Corridor.

21

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

Figure 7: UAM Corridor with Multiple Tracks

4.5  Weather and Obstacles Within the UAM Environment

PSUs or SDSPs support the UAM operator by supplying weather, terrain, and obstacle clearance
data specific to the UAM operation. This data is accessed in the UAM Operational Intent planning
phase to ensure strategic management of a UAM operation and updated in-flight, as appropriate.
UAM operators monitor weather and winds prior to and throughout flight. If aircraft performance
is  inadequate  to  maintain  required  separation  within  the  UAM  Corridor,  UAM  operators  are
responsible to take appropriate action to ensure separation is maintained (e.g., do not take off, exit
the UAM Corridor, operate per appropriate airspace rules).

4.6

Constraint Information and Advisories

UAM operators are responsible for identifying operational conditions or flight hazards that may
affect an operation. This information is collected and assessed both prior to and during flight to
ensure the safe conduct of the flight. PSUs support this UAM operator responsibility by supplying
information and advisories including, but not limited to:

?  Other airborne traffic including operations within and crossing UAM Corridors.
?  Weather and winds.
?  Other hazards pertinent to low-altitude flight (e.g., obstacles such as a crane or powerline

Notice to Air Missions (NOTAM), bird activity, local restrictions).

?  SAA status.
?  UAM Corridor availability.

22

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

The sharing of projected demand and available capacity information between ATS and federated
service network supports the applicable flow management function (e.g., TFM, CFM). Constraints
may be shared from one environment to be complied with by the other, consistent with applicable
procedures, COPs, and regulations.

5

Notional Architecture

Within the UAM cooperative management environment, the FAA would maintain regulatory and
operational  authority  for  airspace  and  traffic  operations.  UAM  operations  may  be  organized,
coordinated, and managed by a federated set of actors through a distributed network that leverages
interoperable information systems. Figure 8 depicts a notional architecture of the UAM actors and
contextual relationships and information flows. This architecture is based on patterns established
within  the  UTM  architecture  described  in  the  UTM  ConOps  [2]  and  is  consistent  with  the
architecture described in the ETM ConOps [3].

The federated service network, comprised of individual PSUs operating as a collective, lies at the
center of the UAM notional architecture and exchanges data with UAM operators, USSs, SDSPs,
the  FAA,  and  public  interest  stakeholders.  PSUs  receive  supplemental  data  supporting  UAM
operation management from the SDSPs and provide relevant UAM operational data to the public.
PSUs  communicate  and  coordinate  via  the  federated  service  network.  This  allows  other  UAM
stakeholders  (e.g., UAM  operators, ATC,  law  enforcement) connected to a PSU to access data
shared across the federated service network.

PSUs  and  USSs  may  exchange  operational  information  about  UAM  and  UTM  operations  in
airspace under 400 feet where there is a potential need for cooperative separation (e.g., vertiports).
Notionally, a USS can expand their service offerings to become a PSU and vice versa. Combined
service  providers  may  support  operations  in  both  the  UAM  and  UTM  environments.  The
architecture  depicts  the  connectivity  of  the  federated  service  network  to  USSs  for  information
exchange while retaining a UAM-centric architectural view.

information  with

Vertiports  exchange
the
communication of situational awareness and resourcing information to UAM operators. The PSUs
make the aggregate vertiport information available for the operator to be aware of capacity and
situational  constraints  present  at  the  time  of  respective  departure  and  arrival  time.  PSUs  could
potentially provide additional services with this information (e.g., suggested alternate vertiports,
suggested alternate departure/arrival times).

the  federated  service  network

to  facilitate

The vertical dashed line  in Figure 8 represents the demarcation between the FAA and industry
responsibilities for the infrastructure, services, and entities that interact as part of UAM. The FAA-
Industry Data Exchange Protocol provides an interface for the FAA to request UAM operational
data on demand and send FAA information to the federated service network for distribution to
UAM operators, PICs, UAM aircraft, and public interest stakeholders through the Service Security
Gateway.

23

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

Figure 8: Notional UAM Architecture

5.1

Supporting Services

UAM services that may be provided by PSUs and SDSPs are intended to be modular and discrete,
allowing for increased flexibility in the design and implementation of new services. This modular
approach would allow the FAA to provide tailored oversight of UAM operations and allows PSUs
and SDSPs to provide focused services consistent with a business model and subscriber needs.
Similar to UTM, UAM services may be characterized in one of the following ways.

1.  Services that are required to be used by UAM operators due to FAA regulation or for a
direct connection to FAA systems. These services must be qualified and approved by the
FAA.

2.  Services that may be used by a UAM operator to meet all or part of an FAA regulation.
These  services  must  meet  an  acceptable  means  of  compliance  and  may  be  individually
qualified and approved by the FAA.

3.  Services that provide value-added assistance to a UAM operator but are not used for FAA
regulatory  compliance.  These  services  may  meet  an  industry  standard  but  may  not  be
qualified or approved by the FAA.

6

UAM Scenarios

This section provides high-level scenarios reflecting two operations. The first is conducted from
departure to arrival within a UAM Corridor. The second operation departs a vertiport in the current
Class B service environment (ATS), enters a UAM Corridor for a portion of the flight, exits back
into Class B (ATS) and arrives at the vertiport. These scenarios further explore the UAM concept

24

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

and each steps through phases of the flight＊s operation, illustrating the operational and architectural
information from Sections 4 and 5.

The scenarios demonstrate a subset of UAM operations and interactions during specific nominal
operations. A nominal UAM operation is a single UAM operation that executes in accordance with
the established performances, rules, policies, and procedures.

6.1

Nominal UAM Operation Completed Within a UAM Corridor

6.1.1

Planning Phase

Planning of this operation starts with the UAM operator receiving a request from an individual
flight between Vertiport 1 and Vertiport 2.

The UAM operator obtains current conditions from the information provided by the subscribed
PSU and relevant SDSP service. After determining that the current conditions are acceptable for
the  operation,  the  UAM  operator  submits  desired  UAM  Operational  Intent  information  (e.g.,
identifying information, vertiport locations, route of flight via UAM Corridor(s), desired time of
operation) to the subscribed PSU.

The PSU, through the federated service network:

1.  Evaluates the desired UAM Operational Intent against other operations that may cause a

strategic conflict.

2.  Evaluates  UAM  Operational  Intent  against  known  airspace  constraints  (e.g.,  FAA

originating constraints, local restrictions).

3.  Identifies availability of UAM Corridors and UAM vertiport resources.

Because  there  are  no  conflicting  operations,  airspace  restrictions  (e.g.,  Temporary  Flight
Restrictions  [TFRs]),  or  vertiport  resource  limitations,  the  UAM  operator＊s  desired  UAM
Operational Intent is considered strategically deconflicted and confirmed. The PSU notifies the
UAM operator and provides the UAM Operational Intent to the federated service network.

The UAM operator considers possible modifications to the Operational Intent in the event of an
off-nominal situation. The airspace classes and ATC facilities with jurisdiction for the airspaces
that border the UAM Corridor(s) for the operation are identified. These prepare the PIC in case a
contingency operation is required.

Most of the planning actions and information exchanges between the UAM operator and PSU are
automated and expected to take very little time from the initial customer request to the confirmed
UAM Operational Intent.

6.1.2

In-Flight Phases

Throughout  all  phases  of  flight,  the  UAM  aircraft  identification  and  location  information  are
available to the UAM operator and subscribed PSU. The PIC and UAM operator monitor aircraft

25

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

performance  to  ensure  nominal  operation  status  is  maintained.  The  PSU  monitors  Operational
Intent conformance.

6.1.2.1  Departure Phase

The PIC departs from Vertiport 1 within the departure compliance window and enters the UAM
Corridor.

6.1.2.2  En Route Phase

The PIC navigates along the UAM Corridor per the UAM Operational Intent. The UAM aircraft
completes the en route portion of the flight per the UAM Operational Intent and approaches the
arrival vertiport within the compliance window of the arrival time.

6.1.2.3  Arrival Phase

As the UAM aircraft approaches Vertiport 2, the PIC, UAM operator, PSU, and UAM vertiport
confirm the landing pad is still available per the UAM Operational Intent. The PIC navigates to
the allocated vertiport pad and lands the aircraft.

6.1.3

Post-Operations Phase

The UAM operator and PIC provide mission complete indication to the PSU. The PSU archives
required UAM operational data per regulation.

6.2

Nominal UAM Operation Across Service Environments

This scenario describes a situation where a UAM operator plans a flight that departs from Vertiport
3, located in Class B airspace, and arrives at Vertiport 4, within Class B airspace, after using a
UAM Corridor for transit. The operator enters and exits the UAM service environment through
CEPs.  Confirmed  UAM  Operational  Intent  is  required  for  participation  within  the  UAM
environment. The UAM operators utilize a PSU who provides flight plan filing services.

6.2.1

Planning Phase

Planning of this operation starts with the UAM operator receiving a request from an individual
customer  for  a  flight  between  Vertiport  3  and  Vertiport  4.  The  UAM  operator  obtains  current
conditions and vertiport availability from their subscribed PSU as well as relevant SDSP services
(e.g., environment, situational awareness, strategic operational demand, supplemental data).

After  determining  the  current  conditions  are  acceptable  for  the  operation,  the  UAM  operator
provides the necessary information to the PSU. In this case, the operation will use a UAM Corridor
that traverses Class B airspace and operate within the Class B airspace to/from the UAM Corridor.
In  recognition  of  the  cross-service  environment  operation,  the  operator＊s  information  for  the
portion of the flight planned for the UAM Corridor includes the desired UAM Operational Intent
information (e.g., identifying information, vertiport locations, route of flight via UAM Corridor(s),
CEP locations, desired time of operation). As the operation, upon departure, will operate in Class
B airspace, the operator also provides the PSU the required flight plan information for the ATS

26

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

environment (e.g., flight ID, type of aircraft, route to CEP from departure vertiport, route from
CEP to arrival vertiport). The PSU uses the flight plan information to coordinate with TFM and
CFM services to secure clearance times and slot reservations for CEPs within the CA.

The subscribed PSU transmits the applicable information (e.g., flight information, flight plan) to
the relevant ATS/xTM data exchange network as required by relevant regulations and COPs. The
PSU  receives  information  (e.g.,  ATC/TFM  responses,  notices,  constraints)  from  the  ATS  data
exchange portal for the UAM operator to use for situational awareness or to modify the planned
intent/flight plan.

The PSU, through the federated service network:

1.  Evaluates  the  desired  UAM  Operational  Intent  for  other  operations  that  may  cause  a

strategic conflict.

2.  Evaluates  the  UAM  Operational  Intent  against  known  airspace  constraints  (e.g.,  FAA

originating constraints, local restrictions).

3.  Identifies availability of the UAM Corridor and UAM vertiport resources.

4.  Receives any applicable flow management initiatives or constraints.

5.  Files the flight plan from Vertiport 3 to Vertiport 4 through the UAM Corridor.

If  there  are  no  conflicting  operations,  airspace  restrictions  (e.g.,  TFRs),  applicable  flow
management  constraints  (i.e.,  CFM  and  TFM),  or  vertiport  resource  limitations,  the  UAM
operator＊s desired UAM Operational Intent is considered strategically deconflicted and confirmed.
The  PSU  notifies  the  UAM  operator  and  provides  the  final  UAM  Operational  Intent  to  the
federated service network and flight plan information to the ATS exchange (e.g., Expect Departure
Clearance Time [EDCT]).

Most of the planning actions and information exchanges (e.g., intent, flight plan filing) across the
federated  service  network,  ATS  (i.e.,  ATC  and  TFM),  operator,  and  PSU  are  automated  and
expected  to  take  very  little  time  from  the  initial  customer  request  to  the  confirmed  UAM
Operational Intent and flight plan filing.

6.2.2

In-Flight Phases

Throughout all phases of flight (e.g., departure, en route, arrival) for a UAM operation, the UAM
aircraft identification and location information are available to the UAM operator, ATC facility,
and subscribed PSU. The PIC and UAM operator monitor aircraft performance to identify an off-
nominal  state. The PSU monitors  operational  conformance to the confirmed UAM Operational
Intents. Data exchange between CFM and TFM are monitored for accuracy and relayed to ATC
and the PSU.

6.2.2.1  Departure Phase

Prior to departure, the PIC establishes two-way communication with the appropriate ATC facility
to open the submitted flight plan that was submitted by the PSU. The PIC departs from Vertiport
3 within the departure compliance window, notifies the PSU (via automated departure acquisition),
and enters Class B airspace. The UAM PIC monitors applicable ATC frequencies and complies

27

Urban Air Mobility (UAM)
Concept of Operations

Version 2.0
April 26, 2023

with instructions while in Class B airspace. The UAM aircraft transitions into the UAM Corridor
through the CEP submitted through the Operational Intent.

6.2.2.2  En Route Phase

The PIC navigates along the UAM Corridor per the confirmed UAM Operational Intent. The PIC
deconflicts  from  other  aircraft  within  the  UAM Corridor  with  possible  support  from  the  UAM
aircraft equipage or PSU services (e.g., flight data from active operations in the UAM Corridor).
Flight status is monitored by CFM to TFM and updated as necessary within the system. The UAM
aircraft completes the en route portion of the flight per the UAM Operational Intent and approaches
the CEP within the compliance window of the arrival time.

6.2.2.3  Arrival Phase

Prior to arriving at the submitted CEP to exit the UAM Corridor into Class B airspace, the data
exchange (e.g., handoff) is activated to ATC and frequency change is conducted. The UAM PIC
establishes two-way communication and positive clearance with the appropriate ATC facility. The
UAM aircraft enters Class B airspace through the CEP per ATC instruction.

As the UAM aircraft approaches Vertiport 4, the PIC, UAM operator, PSU, and UAM vertiport
confirm the landing pad is still available per the UAM Operational Intent. The PIC navigates to
the allocated vertiport pad and lands the aircraft.

6.2.3

Post-Operations Phase

The UAM operator/PIC provides mission completion indication to the PSU and the ATC facility.
The PSU archives required UAM operational data.

7

UAM Evolution

The  UAM  ConOps  2.0  reflects  FAA  efforts,  in  collaboration  with  NASA,  industry,  and  other
stakeholders, to advance UAM. It begins with the introduction of low-complexity, low-operational
tempo  operations  leveraging  the  current  regulatory  framework  (e.g.,  VFR,  IFR)  and  building
toward  higher  operational  tempo  with  the  institution  of  UAM  airspace  structures  (i.e.,  UAM
Corridors) where and when operationally advantageous, using a performance-based construct.

As operations occur and experience is  gained, the concept may mature and evolve  as the FAA
continues  to  engage  stakeholders  for  their  perspectives  on  new  technologies,  techniques,  and
automation,  both  ground-based  and  airborne,  to  identify  those  most  capable  of  addressing  the
evolving  challenges  and  opportunities.  This  evolutionary  approach  to  UAM  could  provide
advantages.  By  initially  supporting  lower  complexity  operations,  implementation  can  be
streamlined to the environment using current capabilities that meet performance requirements and
do not require full-scale regulatory and operational infrastructure changes. Incremental changes to
the  regulatory  framework,  ※hard§  infrastructure  (e.g.,  systems  and  vertiports),  and  ※soft§
infrastructure (e.g., processes and procedures) could help support the UAM operational demand
and complexity as they increase in concert with other cooperative environments, such as UTM and
AAM. These incremental changes may also support the progression of the existing ATS system,
maintaining fair and equitable access to airspace across the full airspace user community.

28

Urban Air Mobility (UAM)
Concept of Operations

Appendix A  References

Version 2.0
April 26, 2023

[1]

[2]

[3]

International Civil Aviation Organization (ICAO), Document 9854, Global Air Traffic
Management Operational Concept (GATMOC), First Edition, 2005.

FAA, Unmanned Aircraft System (UAS) Traffic Management (UTM) Concept of
Operations (ConOps) Version 2.0. 2020.

FAA, Upper Class E Traffic Management (ETM) Concept of Operations (ConOps)
Version 1.0. 2020.

29

Version 2.0
April 26, 2023

Urban Air Mobility (UAM)
Concept of Operations

Appendix B  Acronyms

All acronyms used throughout the document are provided in Table 1.

Table 1: Acronyms

Acronym

Definition

AAM

AFR

ATC

ATS

CA

CBR

CEP

CFM

CNS

COP

Advanced Air Mobility

Automated Flight Rule

Air Traffic Control

Air Traffic Services

Cooperative Area

Community Business Rule

Corridor Entry/Exit Point

Cooperative Flow Management

Communication, Navigation, and Surveillance

Cooperative Operating Practice

ConOps

Concept of Operations

DCB

DEP

DOT

EDCT

ETM

eVTOL

FAA

G/G

HOTL

HOVTL

HWTL

IFR

IMC

LOA

MRO

Demand-Capacity Balancing

Distributed Electric Propulsion

Department of Transportation

Expect Departure Clearance Time

Upper Class E Traffic Management

Electric Vertical Takeoff and Landing

Federal Aviation Administration

Ground-to-Ground

Human-on-the-Loop

Human-Over-the-Loop

Human-Within-the-Loop

Instrument Flight Rules

Instrument Meteorological Conditions

Letter of Agreement

Maintenance, Repair, and Overhaul

30

Urban Air Mobility (UAM)
Concept of Operations

Acronym

Definition

Version 2.0
April 26, 2023

NAS

NASA

NOTAM

PIC

PSU

RPIC

SAA

SDSP

TFM

TFR

UAM

UAS

USS

UTM

V2V

VFR

VMC

VTOL

xTM

National Airspace System

National Aeronautics and Space Administration

Notice to Air Missions

Pilot in Command

Provider of Services for UAM

Remote Pilot in Command

Special Activity Airspace

Supplemental Data Service Provider

Traffic Flow Management

Temporary Flight Restriction

Urban Air Mobility

Unmanned Aircraft Systems

UAS Service Supplier

UAS Traffic Management

Vehicle-to-Vehicle

Visual Flight Rules

Visual Meteorological Conditions

Vertical Takeoff and Landing

Extensible Traffic Management

31

Urban Air Mobility (UAM)
Concept of Operations

Appendix C  Glossary

Version 2.0
April 26, 2023

Table  2  provides  a  glossary  of  UAM  terms  used  throughout  this  ConOps.  These  terms  are  in
addition to those defined in Section 1.4, which provides terms key to establishing the context of
the UAM concept.

Table 2: Glossary

Acronym

Definition

Advanced Air
Mobility (AAM)

Conflict

Constraint

Cooperative
Separation

Demand-Capacity
Balancing (DCB)

The terms ※advanced air mobility§ and ※AAM§ mean a
transportation system that transports people and property by air
between two points in the United States using aircraft with advanced
technologies, including electric aircraft or electric vertical take-off
and landing aircraft, in both controlled and uncontrolled airspace.

Any situation involving aircraft and hazards in which the applicable
separation minima may be compromised [1].

An impact to the capacity or use of a resource preferred by an
operator, defined with time and geographically specified airspace
information. A constraint may restrict access to airspace for
operations or may be advisory in nature.

Separation based on shared flight intent and data exchanges between
operators, stakeholders, and service providers. Cooperative
separation is supported by defined COPs as well as applicable rules,
regulations, and policies.

Strategic evaluation of system-wide traffic flows and aerodrome
capacities to allow airspace users to determine when, where, and how
they operate, while mitigating conflicting needs for airspace and
aerodrome capacity. This collaborative process allows for the
efficient management of air traffic flow through the use of
information on system-wide air traffic flows, weather, and assets [1].

Human-on-the-Loop
(HOTL)

Human supervisory control of the automation (i.e., systems) where
the human actively monitors the systems and can take full control
when required or desired.

Human-Over-the-
Loop (HOVTL)

Human-Within-the-
Loop (HWTL)

Human informed, or engaged, by the automation (i.e., systems) to
take actions. Human passively monitors the systems and is informed
by automation if, and what, action is required. Human is engaged by
the automation either for exceptions that are not reconcilable or as
part of rule set escalation.

Human is always in direct control of the automation (systems).

32

Urban Air Mobility (UAM)
Concept of Operations

Acronym

Definition

Version 2.0
April 26, 2023

Operational Intent

Also referred to as operation intent, the future operational position
information, consisting of spatial and temporal elements, that is
exchanged between xTM operators to support cooperative traffic
management.

Operational Tempo

The density, frequency, and complexity of operations.

Provider of Services
for UAM (PSU)

Strategic
Deconfliction

Tactical Deconfliction

An entity that assists UAM operators with meeting UAM operational
requirements to enable safe and efficient use of UAM Corridors and
vertiports. This service provider shares operational data with
stakeholders and confirms flight intent.

The process of arranging, negotiating, and prioritizing Operational
Intent (e.g., volumes, routes, trajectories, time assignments) of
aircraft to minimize the likelihood of airborne conflicts between
operations.

The process of executing one or more actions to avoid an airborne
conflict in a timely manner when strategic deconfliction has failed or
was not executed.

UAS Traffic
Management (UTM)

The manner in which the FAA will support operations for UAS
operating in low-altitude airspace.

33


