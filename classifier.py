"""
Hierarchical Job Taxonomy & Classification Engine.
Maps job titles and queries into a 3-tier professional structure:
[Subject Field / Domain] -> [Category] -> [Granular Specialization]

Designed to support granular specialization breakdowns across 1,000+ roles.
"""

import re
from typing import Tuple, List, Dict, Any

# Structure of each taxonomy rule:
# (Subject Field, Category, Granular Specialization, [regex patterns])
TAXONOMY_RULES = [
    # -------------------------------------------------------------
    # 1. SEMICONDUCTOR, VLSI & EMBEDDED HARDWARE
    # -------------------------------------------------------------
    (
        "Semiconductor, VLSI & Hardware",
        "ASIC & SoC Design",
        "ASIC / SoC Verification & RTL Engineer",
        [r"\basic\b", r"\bsoc\b", r"\brtl\b", r"\bverilog\b", r"\bvhdl\b", r"\bvlsi\s+engineer\b", r"\bvlsi\b"]
    ),
    (
        "Semiconductor, VLSI & Hardware",
        "FPGA & Digital Logic",
        "FPGA Design & Digital Systems Engineer",
        [r"\bfpga\b", r"\bdigital\s+logic\b"]
    ),
    (
        "Semiconductor, VLSI & Hardware",
        "PCB & Circuit Hardware",
        "PCB Layout & Circuit Design Engineer",
        [r"\bpcb\b", r"\bcircuit\s+design\b", r"\bprinted\s+circuit\b", r"\baltium\b", r"\bkicad\b"]
    ),
    (
        "Semiconductor, VLSI & Hardware",
        "Embedded Systems & Firmware",
        "Embedded Firmware & Microcontroller Engineer",
        [r"\bembedded\b", r"\bfirmware\b", r"\bmicrocontroller\b", r"\bstm32\b", r"\besp32\b", r"\barduino\b"]
    ),
    (
        "Semiconductor, VLSI & Hardware",
        "IoT & Connected Systems",
        "IoT Systems & Hardware Engineer",
        [r"\biot\b", r"\binternet\s+of\s+things\b"]
    ),
    (
        "Semiconductor, VLSI & Hardware",
        "EDA & Applications",
        "EDA Tools & Applications Engineer (Cadence/Synopsys)",
        [r"\beda\b", r"\bcadence\b", r"\bsynopsys\b", r"\bmentor\s+graphics\b", r"application\s+engineer.*(?:vlsi|hardware|semiconductor|cadence|eda)", r"\bsr\s+application\s+engineer\b"]
    ),
    (
        "Semiconductor, VLSI & Hardware",
        "General Hardware",
        "Hardware Design & Test Engineer",
        [r"\bhardware\s+engineer\b", r"\bsemiconductor\b"]
    ),

    # -------------------------------------------------------------
    # 2. POWER, ENERGY & ELECTRICAL SYSTEMS
    # -------------------------------------------------------------
    (
        "Power, Energy & Electrical",
        "Substation & Switchgear",
        "High Voltage Substation & Switchgear Engineer",
        [r"\bsubstation\b", r"\bswitchgear\b", r"\bhigh\s+voltage\b", r"\btransformer\b", r"\btransmission\b", r"\bpower\s+distribution\b"]
    ),
    (
        "Power, Energy & Electrical",
        "Power Generation & Plants",
        "Power Plant Operations & Grid Engineer",
        [r"\bpower\s+plant\b", r"\bpower\s+generation\b", r"\bpower\s+grid\b", r"\bpower\s+lead\b", r"\bpower\s+engineer\b", r"\bpower\s+electricity\b", r"\bélectricité\s+de\s+puissance\b", r"\bpuissance\b", r"\bpower\s+systems\b"]
    ),
    (
        "Power, Energy & Electrical",
        "Solar & Renewable Energy",
        "Solar PV & Renewable Energy Systems Engineer",
        [r"\bsolar\b", r"\brenewable\b", r"\bpv\s+engineer\b"]
    ),
    (
        "Power, Energy & Electrical",
        "MEP & Building Facilities",
        "MEP (Mechanical, Electrical & Plumbing) Engineer",
        [r"\bmep\b", r"\bbuilding\s+facilities\b"]
    ),
    (
        "Power, Energy & Electrical",
        "Electrical Maintenance",
        "Electrical Maintenance & Plant In-Charge",
        [r"\belectrical\s+maintenance\b", r"\belectrical\s+in-charge\b", r"\bgenerator\b"]
    ),
    (
        "Power, Energy & Electrical",
        "Electrical Technician",
        "Electrician, Wiring & Electrical Technician",
        [r"\belectrician\b", r"\bwiring\b", r"\belectrical\s+technician\b"]
    ),
    (
        "Power, Energy & Electrical",
        "General Electrical",
        "Electrical Systems & Project Engineer",
        [r"\belectrical\s+engineer\b", r"\belectrical\b", r"\belectricity\b", r"\beléctrico\b", r"\bélectrique\b"]
    ),

    # -------------------------------------------------------------
    # 3. CONSTRUCTION, CIVIL & INFRASTRUCTURE
    # -------------------------------------------------------------
    (
        "Construction, Civil & Real Estate",
        "Structural Engineering",
        "Structural Analysis & Design Engineer (ETABS/STAAD)",
        [r"\bstructural\b", r"\betabs\b", r"\bstaad\b", r"\bbridge\s+engineer\b"]
    ),
    (
        "Construction, Civil & Real Estate",
        "Site Supervision & Execution",
        "Civil Site Engineer & Construction Supervisor",
        [r"\bsite\s+engineer\b", r"\bcivil\s+site\b", r"\bpiling\b", r"\bconstruction\s+supervisor\b"]
    ),
    (
        "Construction, Civil & Real Estate",
        "BIM & Architectural CAD",
        "BIM Modeler & Architectural CAD Designer",
        [r"\bbim\b", r"\barchitect\b", r"\barchitecture\b", r"\brevit\b", r"\bautocad\b", r"\binterior\b"]
    ),
    (
        "Construction, Civil & Real Estate",
        "Geotechnical & Foundation",
        "Geotechnical & Soil Mechanics Engineer",
        [r"\bgeotechnical\b", r"\bsoil\s+engineer\b"]
    ),
    (
        "Construction, Civil & Real Estate",
        "Quantity Surveying & Estimation",
        "Quantity Surveyor & Project Estimator (BOQ)",
        [r"\bquantity\s+surveyor\b", r"\bestimator\b", r"\bsurveyor\b", r"\bboq\b"]
    ),
    (
        "Construction, Civil & Real Estate",
        "Real Estate & Project Planning",
        "Real Estate Project Manager & Civil Planner",
        [r"\breal\s+estate\b", r"\bcivil\s+project\b", r"\bcivil\s+engineer\b", r"\bconstruction\b", r"\bcivil\b"]
    ),

    # -------------------------------------------------------------
    # 4. MANUFACTURING, PRODUCTION & MECHANICAL
    # -------------------------------------------------------------
    (
        "Manufacturing, Production & Industrial",
        "Plant & Production Operations",
        "Production Planning & Plant Operations Engineer",
        [r"\bproduction\s+(?:engineer|officer|manager|supervisor|in-charge)\b", r"\bplant\s+(?:engineer|manager)\b", r"\bfactory\s+manager\b"]
    ),
    (
        "Manufacturing, Production & Industrial",
        "Mechanical Maintenance & HVAC",
        "Mechanical Maintenance & HVAC Plant Engineer",
        [r"\bmechanical\s+maintenance\b", r"\bhvac\b", r"\bworkshop\s+expert\b", r"\bboiler\b", r"\bmaintenance\s+head\b"]
    ),
    (
        "Manufacturing, Production & Industrial",
        "Industrial Engineering & Lean",
        "Industrial Engineer & Lean Manufacturing (IE)",
        [r"\bindustrial\s+engineer\b", r"\bipe\b", r"\blean\b", r"\bsix\s+sigma\b", r"\bwork\s+study\b"]
    ),
    (
        "Manufacturing, Production & Industrial",
        "Costing & Industrial Estimation",
        "Production Costing & Industrial Estimation Engineer",
        [r"\bcosting\s+engineer\b", r"\bcosting\b", r"\bestimation\s+engineer\b"]
    ),
    (
        "Manufacturing, Production & Industrial",
        "CNC Machining & Tooling",
        "CNC Machining, Tooling & Fabrication Engineer",
        [r"\bcnc\b", r"\bmachining\b", r"\bfabrication\b", r"\btooling\b", r"\bmechatronics\b"]
    ),
    (
        "Manufacturing, Production & Industrial",
        "Quality Control & QA",
        "Manufacturing Quality Assurance & QC Inspector",
        [r"\bquality\s+control\b", r"\bqc\s+inspector\b", r"\bqa\/qc\b"]
    ),
    (
        "Manufacturing, Production & Industrial",
        "General Mechanical",
        "Mechanical Project & Design Engineer",
        [r"\bmechanical\s+engineer\b", r"\bmechanical\b", r"\bmaintenance\s+engineer\b"]
    ),

    # -------------------------------------------------------------
    # 5. TEXTILE, APPAREL & GARMENTS
    # -------------------------------------------------------------
    (
        "Textile, Garments & Apparel",
        "Apparel Merchandising",
        "Woven & Knit Garments Merchandiser",
        [r"\bmerchandis\w*\b"]
    ),
    (
        "Textile, Garments & Apparel",
        "Wet Processing & Dyeing",
        "Textile Wet Processing & Dyeing Specialist",
        [r"\bdyeing\b", r"\bwash\w*\b", r"\bfinishing\b"]
    ),
    (
        "Textile, Garments & Apparel",
        "Spinning & Fabric Technology",
        "Fabric Sourcing, Yarn & Spinning Specialist",
        [r"\bfabric\b", r"\byarn\b", r"\bspinning\b", r"\bknitting\b", r"\bweaving\b"]
    ),
    (
        "Textile, Garments & Apparel",
        "Pattern Making & Fashion CAD",
        "Pattern Making & Fashion CAD Designer (Gerber/Optitex)",
        [r"\bpattern\s+maker\b", r"\bfashion\s+design\w*\b", r"\bgerber\b", r"\boptitex\b"]
    ),
    (
        "Textile, Garments & Apparel",
        "General Textile",
        "Textile & Apparel Manufacturing Engineer",
        [r"\btextile\s+engineer\b", r"\btextile\b", r"\bgarment\b", r"\bapparel\b"]
    ),

    # -------------------------------------------------------------
    # 6. SOFTWARE, WEB & MOBILE ENGINEERING
    # -------------------------------------------------------------
    (
        "Software & Web Engineering",
        "Backend Engineering",
        "Python / Django / FastAPI Backend Engineer",
        [r"\bpython\b", r"\bdjango\b", r"\bfastapi\b", r"\bflask\b"]
    ),
    (
        "Software & Web Engineering",
        "Backend Engineering",
        "Java / Spring Boot Enterprise Backend Engineer",
        [r"\bjava\b", r"\bspring\s*boot\b"]
    ),
    (
        "Software & Web Engineering",
        "Backend Engineering",
        "Golang / Distributed Systems Backend Engineer",
        [r"\bgolang\b", r"\bgo\s+developer\b"]
    ),
    (
        "Software & Web Engineering",
        "Backend Engineering",
        ".NET / C# Enterprise Backend Engineer",
        [r"\b\.net\b", r"\bc#\b", r"\basp\.net\b"]
    ),
    (
        "Software & Web Engineering",
        "Backend Engineering",
        "PHP / Laravel Backend Engineer",
        [r"\bphp\b", r"\blaravel\b"]
    ),
    (
        "Software & Web Engineering",
        "Backend Engineering",
        "Node.js / Express Server-Side Engineer",
        [r"\bnode\.?js\b", r"\bexpress\.?js\b"]
    ),
    (
        "Software & Web Engineering",
        "Frontend Engineering",
        "React / Next.js Modern Frontend Engineer",
        [r"\breact\.?js\b", r"\breact\b", r"\bnext\.?js\b"]
    ),
    (
        "Software & Web Engineering",
        "Frontend Engineering",
        "Vue / Angular Frontend Engineer",
        [r"\bvue\.?js\b", r"\bvue\b", r"\bangular\b"]
    ),
    (
        "Software & Web Engineering",
        "Full Stack Engineering",
        "Full Stack Web Application Engineer",
        [r"\bfull[\s\-]*stack\b"]
    ),
    (
        "Software & Web Engineering",
        "Mobile App Development",
        "Flutter Cross-Platform Mobile Engineer",
        [r"\bflutter\b", r"\bdart\b"]
    ),
    (
        "Software & Web Engineering",
        "Mobile App Development",
        "Native Android / iOS Mobile Engineer (Kotlin/Swift)",
        [r"\bandroid\b", r"\bios\b", r"\bkotlin\b", r"\bswift\b", r"\breact\s+native\b", r"\bmobile\s+app\b", r"\bmobile\s+developer\b"]
    ),
    (
        "Software & Web Engineering",
        "General Frontend",
        "Frontend UI & Client-Side Web Developer",
        [r"\bfrontend\b", r"\bfront-end\b", r"\bweb\s+developer\b"]
    ),
    (
        "Software & Web Engineering",
        "General Backend",
        "Backend API & Database Engineer",
        [r"\bbackend\b", r"\bback-end\b"]
    ),
    (
        "Software & Web Engineering",
        "General Software",
        "Software Development Engineer (Core SDE)",
        [r"\bsoftware\s+engineer\b", r"\bsoftware\s+developer\b", r"\bprogrammer\b", r"\bc\+\+\b", r"\bcode\s+reviewer\b"]
    ),

    # -------------------------------------------------------------
    # 7. AI, MACHINE LEARNING & DATA SCIENCE
    # -------------------------------------------------------------
    (
        "AI, Machine Learning & Data",
        "Computer Vision & Imaging",
        "Computer Vision & Visual Reconstruction Engineer",
        [r"\bvisual\s+reconstruction\b", r"\bimage-to-code\b", r"\bcomputer\s+vision\b", r"\bopencv\b", r"\bimage\s+processing\b"]
    ),
    (
        "AI, Machine Learning & Data",
        "Generative AI & LLMs",
        "LLM & Generative AI Systems Engineer",
        [r"\bllm\b", r"\bgenerative\s+ai\b", r"\blangchain\b"]
    ),
    (
        "AI, Machine Learning & Data",
        "Machine Learning & Deep Learning",
        "Machine Learning & Deep Learning Engineer",
        [r"\bmachine\s+learning\b", r"\bdeep\s+learning\b", r"\bai\s+engineer\b", r"\bai\s+research\b", r"\bartificial\s+intelligence\b", r"\bnlp\b", r"\bcomputer\s+vision\b", r"\btensorflow\b", r"\bpytorch\b"]
    ),
    (
        "AI, Machine Learning & Data",
        "Data Engineering",
        "Data Pipeline & Big Data Engineer (ETL/Spark)",
        [r"\bdata\s+engineer\b", r"\bbig\s+data\b", r"\bspark\b", r"\betl\b", r"\bdata\s+pipeline\b"]
    ),
    (
        "AI, Machine Learning & Data",
        "Business Intelligence & Analytics",
        "Data Scientist & Analytics Specialist",
        [r"\bdata\s+scientist\b", r"\bresearch\s+scientist\b", r"\bdata\s+analyst\b", r"\bdata\s+science\b", r"\bpower\s+bi\b", r"\btableau\b", r"\bbi\s+developer\b"]
    ),

    # -------------------------------------------------------------
    # 8. CLOUD, DEVOPS & INFRASTRUCTURE
    # -------------------------------------------------------------
    (
        "Cloud, DevOps & Infrastructure",
        "Platform & Systems Engineering",
        "Platform Infrastructure & Systems Engineer",
        [r"\bplatform\s+engineer\b", r"\binfrastructure\s+engineer\b", r"\bcloud\s+platform\b"]
    ),
    (
        "Cloud, DevOps & Infrastructure",
        "IT Support & Administration",
        "IT Support & Enterprise Systems Administrator",
        [r"\bit\s+support\b", r"\bhelpdesk\b", r"\bdesktop\s+support\b", r"\bit\s+executive\b", r"\bit\s+officer\b", r"\bit\s+specialist\b"]
    ),
    (
        "Cloud, DevOps & Infrastructure",
        "Cloud Architecture",
        "Cloud Solutions Architect (AWS/Azure/GCP)",
        [r"\bcloud\s+engineer\b", r"\bcloud\s+architect\b", r"\baws\b", r"\bazure\b", r"\bgcp\b"]
    ),
    (
        "Cloud, DevOps & Infrastructure",
        "DevOps & Automation",
        "DevOps & CI/CD Platform Engineer",
        [r"\bdevops\b", r"\bci\/cd\b", r"\bterraform\b", r"\bjenkins\b"]
    ),
    (
        "Cloud, DevOps & Infrastructure",
        "Site Reliability (SRE)",
        "Site Reliability Engineer & Kubernetes Specialist",
        [r"\bkubernetes\b", r"\bdocker\b", r"\bsre\b", r"\bsite\s+reliability\b"]
    ),
    (
        "Cloud, DevOps & Infrastructure",
        "Systems Administration",
        "Linux & Enterprise Systems Administrator",
        [r"\bsystem\s+admin\b", r"\bsysadmin\b", r"\blinux\s+admin\b", r"\bserver\s+admin\b", r"\boss\s+specialist\b"]
    ),

    # -------------------------------------------------------------
    # 9. CYBERSECURITY & NETWORK SYSTEMS
    # -------------------------------------------------------------
    (
        "Cybersecurity & Networks",
        "SOC & Threat Intelligence",
        "SOC Security Analyst & Incident Responder",
        [r"\bsoc\s+analyst\b", r"\bsoc\b", r"\bincident\s+response\b"]
    ),
    (
        "Cybersecurity & Networks",
        "Offensive Security",
        "Penetration Tester & Vulnerability Assessor",
        [r"\bpenetration\s+test\b", r"\bpentester\b", r"\bethical\s+hack\w*\b", r"\bvulnerability\b"]
    ),
    (
        "Cybersecurity & Networks",
        "Enterprise Security & Governance",
        "Information Security Officer & CISO",
        [r"\binformation\s+security\b", r"\bciso\b", r"\bsecurity\s+analyst\b", r"\bcyber\s*security\b"]
    ),
    (
        "Cybersecurity & Networks",
        "Network Engineering",
        "Network Infrastructure & Cisco Security Engineer",
        [r"\bnetwork\s+engineer\b", r"\bcisco\b", r"\bccna\b", r"\bfirewall\b", r"\bnetwork\s+admin\b"]
    ),

    # -------------------------------------------------------------
    # 10. QUALITY ASSURANCE & TESTING (SQA)
    # -------------------------------------------------------------
    (
        "Quality Assurance (SQA)",
        "Test Automation",
        "Test Automation Engineer (Selenium/Playwright/Cypress)",
        [r"\bqa\s+automation\b", r"\bautomation\s+tester\b", r"\bautomation\s+engineer\b", r"\(automation\)", r"\bautomation\b", r"\bselenium\b", r"\bcypress\b", r"\bplaywright\b"]
    ),
    (
        "Quality Assurance (SQA)",
        "Software Quality Assurance",
        "SQA Engineer & Quality Process Specialist",
        [r"\bsqa\b", r"\bqa\s+engineer\b", r"\bquality\s+assurance\b", r"\bqa\b"]
    ),
    (
        "Quality Assurance (SQA)",
        "Functional & Manual Testing",
        "Manual Test Engineer & Quality Analyst",
        [r"\bsoftware\s+tester\b", r"\bmanual\s+tester\b", r"\bqa\s+analyst\b", r"\btest\s+case\b"]
    ),

    # -------------------------------------------------------------
    # 11. DESIGN, UI/UX & CREATIVE MEDIA
    # -------------------------------------------------------------
    (
        "Design, UI/UX & Creative",
        "Product & UI/UX Design",
        "UI/UX & Product Design Specialist",
        [r"\bui\/ux\b", r"\bux\s+designer\b", r"\bui\s+designer\b", r"\bproduct\s+designer\b", r"\bfigma\b"]
    ),
    (
        "Design, UI/UX & Creative",
        "Graphic & Brand Design",
        "Graphic & Brand Identity Designer",
        [r"\bgraphic\s+design\w*\b", r"\bvisual\s+designer\b", r"\bbrand\s+designer\b", r"\bcreative\s+designer\b"]
    ),
    (
        "Design, UI/UX & Creative",
        "3D & Motion Graphics",
        "3D Artist, Video Editor & Motion Graphics Designer",
        [r"\bvideo\s+editor\b", r"\b3d\s+artist\b", r"\banimat\w*\b", r"\bmotion\s+graphic\b", r"\bblender\b"]
    ),

    # -------------------------------------------------------------
    # 12. AVIATION, MARINE & AUTOMOTIVE
    # -------------------------------------------------------------
    (
        "Aviation, Marine & Automotive",
        "Aviation Maintenance",
        "CAMO & Aircraft Technical Records Engineer",
        [r"\bcamo\b", r"\baviation\b", r"\baircraft\b", r"\baeronautical\b", r"\bpilot\b", r"\bflight\b"]
    ),
    (
        "Aviation, Marine & Automotive",
        "Marine Engineering",
        "Marine Engineer & Naval Architect",
        [r"\bmarine\s+engineer\b", r"\bnaval\s+architect\b", r"\bship\b"]
    ),
    (
        "Aviation, Marine & Automotive",
        "Automotive Engineering",
        "Automotive Design & Maintenance Engineer",
        [r"\bautomotive\b", r"\bautomobile\b"]
    ),
    (
        "Aviation, Marine & Automotive",
        "Vehicle & Fleet Maintenance",
        "Vehicle Technician & Fleet Mechanic",
        [r"\bvehicle\s+technician\b", r"\bmechanic\b", r"\bfleet\s+technician\b"]
    ),

    # -------------------------------------------------------------
    # 13. PRODUCT & PROJECT MANAGEMENT
    # -------------------------------------------------------------
    (
        "Product & Project Management",
        "Product Management",
        "Technical Product Manager & Product Owner",
        [r"\bproduct\s+manager\b", r"\bproduct\s+owner\b"]
    ),
    (
        "Product & Project Management",
        "Project & Agile Delivery",
        "Agile Project Manager & Scrum Master",
        [r"\bproject\s+manager\b", r"\bscrum\s+master\b", r"\bagile\s+coach\b", r"\bprogram\s+manager\b"]
    ),

    # -------------------------------------------------------------
    # 14. FINANCE, BANKING & ACCOUNTING
    # -------------------------------------------------------------
    (
        "Finance, Accounting & Tax",
        "Tax & VAT Compliance",
        "Corporate Tax, VAT & Regulatory Specialist",
        [r"\bvat\b", r"\btax\b", r"\btaxation\b"]
    ),
    (
        "Finance, Accounting & Tax",
        "Audit & Financial Control",
        "Internal Audit & Financial Controller",
        [r"\baudit\b", r"\bauditor\b", r"\bcompliance\b"]
    ),
    (
        "Finance, Accounting & Tax",
        "General Accounting",
        "Corporate Accountant & Financial Reporting Specialist",
        [r"\baccountant\b", r"\baccounts\b", r"\baccounting\b", r"\bfinance\b", r"\bfinancial\b", r"\bbilling\b", r"\bcompany\s+secretary\b"]
    ),
    (
        "Finance, Accounting & Tax",
        "Banking & Credit",
        "Core Banking & Credit Risk Specialist",
        [r"\bbanking\b", r"\bbank\b", r"\bcredit\b", r"\bloan\b"]
    ),

    # -------------------------------------------------------------
    # 15. SUPPLY CHAIN & LOGISTICS
    # -------------------------------------------------------------
    (
        "Supply Chain & Logistics",
        "Procurement & Sourcing",
        "Strategic Procurement & Commercial Sourcing Specialist",
        [r"\bprocurement\b", r"\bsourcing\b", r"\bcommercial\b"]
    ),
    (
        "Supply Chain & Logistics",
        "Logistics & Freight",
        "Logistics, Freight & Customs Clearance Specialist (EXIM)",
        [r"\blogistics\b", r"\bwarehouse\b", r"\bfreight\b", r"\bexport\s+import\b", r"\bexim\b"]
    ),
    (
        "Supply Chain & Logistics",
        "Supply Chain Planning",
        "Supply Chain Operations & Inventory Planner",
        [r"\bsupply\s+chain\b", r"\binventory\b"]
    ),

    # -------------------------------------------------------------
    # 16. SALES, MARKETING & BUSINESS DEVELOPMENT
    # -------------------------------------------------------------
    (
        "Sales, Marketing & BD",
        "Digital Marketing & Growth",
        "Digital Marketing, SEO & Growth Specialist",
        [r"\bdigital\s+marketing\b", r"\bseo\b", r"\bsocial\s+media\b", r"\bcontent\s+writer\b", r"\bcopywriter\b", r"\bgrowth\s+hacker\b", r"\bmedia\s+buying\b"]
    ),
    (
        "Sales, Marketing & BD",
        "Corporate Sales & Accounts",
        "Corporate Sales & Business Development Manager",
        [r"\bsales\b", r"\bbusiness\s+development\b", r"\baccount\s+manager\b", r"\btelesales\b", r"\bbrand\s+manager\b"]
    ),

    # -------------------------------------------------------------
    # 17. HR & TALENT ACQUISITION
    # -------------------------------------------------------------
    (
        "HR, Talent Acquisition & Admin",
        "Talent Acquisition",
        "Technical Recruiter & Talent Acquisition Specialist",
        [r"\btalent\s+acquisition\b", r"\brecruiter\b", r"\brecruitment\b"]
    ),
    (
        "HR, Talent Acquisition & Admin",
        "People & HR Operations",
        "HR Generalist & Employee Relations Specialist",
        [r"(?<!\/)(?<!per\s)\bhr\b(?!\/)(?!\s*rate)(?!\s*salary)", r"\bhuman\s+resources\b", r"\bpayroll\b"]
    ),
    (
        "HR, Talent Acquisition & Admin",
        "Administration & Facilities",
        "Office Administrator & Executive Coordinator",
        [r"\badmin\s+executive\b", r"\boffice\s+admin\b", r"\breceptionist\b", r"\bexecutive\s+assistant\b"]
    ),

    # -------------------------------------------------------------
    # 18. HEALTHCARE & PHARMA
    # -------------------------------------------------------------
    (
        "Healthcare, Medical & Pharma",
        "Pharmaceuticals",
        "Pharmaceutical Production & Quality Officer",
        [r"\bpharma\b", r"\bpharmacist\b"]
    ),
    (
        "Healthcare, Medical & Pharma",
        "Clinical & Medical Care",
        "Medical Officer & Clinical Specialist",
        [r"\bdoctor\b", r"\bphysician\b", r"\bnurse\b", r"\bmedical\b", r"\bhospital\b", r"\bclinical\b", r"\bbiochemist\b"]
    ),

    # -------------------------------------------------------------
    # 19. TELECOMMUNICATIONS & ISP
    # -------------------------------------------------------------
    (
        "Telecommunications & ISP",
        "Telecom Network Operations",
        "Telecom RF, Microwave & Transmission Engineer",
        [r"\btelecom\b", r"\btelecommunication\b", r"\brf\s+engineer\b", r"\bbts\b", r"\bmicrowave\b", r"\bfiber\s+optic\b", r"\bnoc\s+engineer\b"]
    ),

    # -------------------------------------------------------------
    # 20. RETAIL, HOSPITALITY & CONSUMER SERVICES
    # -------------------------------------------------------------
    (
        "Retail, Hospitality & Services",
        "Store & Branch Operations",
        "Retail Store Manager & Operations Supervisor",
        [r"\bstore\s+manager\b", r"\bgeneral\s+manager\b", r"\bshift\s+manager\b", r"\bbranch\s+manager\b", r"\bmerchandising\s+associate\b", r"\bmerhcandising\b", r"\bretail\b", r"\bstore\s+associate\b", r"\bshop\s+manager\b", r"\bassistant\s+store\s+manager\b"]
    ),
    (
        "Retail, Hospitality & Services",
        "Food & Hospitality Services",
        "Food Service Specialist, Culinary & Crew Member",
        [r"\bfood\s+service\b", r"\brestaurant\b", r"\bchef\b", r"\bcook\b", r"\bdishwasher\b", r"\bcrew\s+member\b", r"\bbarista\b", r"\bwaiter\b", r"\bwaitress\b", r"\bhost\b", r"\bhostess\b", r"\bkitchen\b", r"\bbartender\b"]
    ),
    (
        "Retail, Hospitality & Services",
        "Customer Support & Client Care",
        "Customer Care & Client Support Executive",
        [r"\bcustomer\s+support\b", r"\bcustomer\s+service\b", r"\bcall\s+center\b", r"\bcontact\s+center\b", r"\bclient\s+support\b", r"\bcustomer\s+care\b"]
    ),
    (
        "Retail, Hospitality & Services",
        "Personal Care & Grooming",
        "Salon, Barber & Lifestyle Associate",
        [r"\bbarber\b", r"\bsalon\b", r"\bhairstylist\b", r"\besthetician\b", r"\bspa\b"]
    ),

    # -------------------------------------------------------------
    # 21. EDUCATION, ACADEMIA & TRAINING
    # -------------------------------------------------------------
    (
        "Education, Academia & Training",
        "Higher Education & Research",
        "University Lecturer, Professor & Faculty",
        [r"\bprofessor\b", r"\blecturer\b", r"\bfaculty\b", r"\bresearch\s+fellow\b", r"\bpostdoc\b", r"\bdean\b"]
    ),
    (
        "Education, Academia & Training",
        "School & Instructional Teaching",
        "School Teacher, Tutor & Academic Instructor",
        [r"\bteacher\b", r"\btutor\b", r"\binstructor\b", r"\bprincipal\b", r"\bcurriculum\b"]
    ),
    (
        "Education, Academia & Training",
        "Corporate Training & L&D",
        "Learning & Development Specialist",
        [r"\blearning\s+and\s+development\b", r"\bl&d\b", r"\btrainer\b"]
    ),

    # -------------------------------------------------------------
    # 22. LEGAL, REGULATORY & CORPORATE GOVERNANCE
    # -------------------------------------------------------------
    (
        "Legal, Regulatory & Governance",
        "Corporate Legal Counsel",
        "Corporate Lawyer & Legal Advisor",
        [r"\blawyer\b", r"\badvocate\b", r"\blegal\s+counsel\b", r"\blegal\s+officer\b", r"\blegal\s+advisor\b", r"\battorney\b", r"\blegal\s+manager\b"]
    ),
    (
        "Legal, Regulatory & Governance",
        "Regulatory Affairs & Compliance",
        "Regulatory Affairs & Compliance Officer",
        [r"\bcompliance\s+officer\b", r"\bregulatory\s+affairs\b", r"\baml\b", r"\bgovernance\s+officer\b"]
    )
]


def classify_job_title(title: str, search_query: str = "") -> Tuple[str, str, str]:
    """
    Classifies a job post into the 3-tier hierarchy:
    (Subject Field / Domain, Category, Granular Specialization)

    Example:
    'Printed Circuit Board Designer' -> (
        'Semiconductor, VLSI & Hardware',
        'PCB & Circuit Hardware',
        'PCB Layout & Circuit Design Engineer'
    )
    'Senior Structural Engineer' -> (
        'Construction, Civil & Real Estate',
        'Structural Engineering',
        'Structural Analysis & Design Engineer (ETABS/STAAD)'
    )
    """
    if not title:
        return ("General & Other Vacancies", "General Support", "General Office Vacancy")

    clean_title = title.lower()

    # Priority match on title
    for subject_field, category, specialization, patterns in TAXONOMY_RULES:
        for pat in patterns:
            if re.search(pat, clean_title, re.IGNORECASE):
                return (subject_field, category, specialization)

    # Fallback to search query if title was vague
    if search_query:
        clean_sq = search_query.lower()
        for subject_field, category, specialization, patterns in TAXONOMY_RULES:
            for pat in patterns:
                if re.search(pat, clean_sq, re.IGNORECASE):
                    return (subject_field, category, specialization)

    return ("General & Other Vacancies", "General Support", "General Technical & Administrative Vacancy")


if __name__ == "__main__":
    test_cases = [
        "Printed Circuit Board Designer",
        "Senior Structural Engineer",
        "Python Backend Developer",
        "High Voltage Substation In-Charge",
        "Apparel Garments Merchandiser",
        "Quality Assurance Engineer (Automation)",
        "CAMO Technical Engineer",
        "AI Research Scientist",
        "DevOps Cloud Engineer"
    ]
    for tc in test_cases:
        fld, cat, spec = classify_job_title(tc)
        print(f"[{fld}] > [{cat}] > {spec}")
