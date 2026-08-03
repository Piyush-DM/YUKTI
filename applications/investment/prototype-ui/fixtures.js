/*
 * Mock-only fixture data for the investment prototype UI.
 *
 * This file is the entire data boundary for the prototype. It intentionally
 * contains no backend client, persistence contract, reasoning logic, model
 * call, provider integration, or DAALE engine import.
 */

window.YUKTI_INVESTMENT_FIXTURES = {
  cases: [
    {
      caseId: "mock-case-northstar-grid-2026-07-16",
      title: "Northstar Grid Infrastructure Series C",
      company: "Northstar Grid Infrastructure",
      ticker: "Private",
      sector: "Grid software and distributed energy operations",
      geography: "United States",
      sponsor: "YUKTI Investment Committee",
      owner: "Anika Rao",
      createdAt: "2026-07-12",
      stage: "Completed mock analysis",
      requestedDecision: "Approve a $12M primary allocation with governance conditions",
      investmentType: "Growth equity",
      timeHorizon: "5-7 years",
      mandateFit: "Energy transition infrastructure, resilient cash-flow software",
      investmentThesis:
        "Northstar sells grid orchestration software to regional utilities and commercial microgrid operators. The mock case tests whether durable contracted revenue, regulatory tailwinds, and measurable deployment efficiency justify a growth investment despite customer concentration and procurement-cycle risk.",
      reasoningModel:
        "Evidence -> RIK Positions -> Conflicts -> Decision Ledger. All relationships are static fixture links for product evaluation only.",
      evidence: [
        {
          id: "EV-001",
          title: "ARR cohort retention schedule",
          source: "Mock management data room",
          sourceType: "Management data room",
          date: "2026-06-30",
          extractedFact:
            "Net revenue retention for the 2024 utility cohort is shown as 126%, with no logo churn in the period reviewed.",
          provenance: "Data room file MDR-14, worksheet Cohort_RET_2024",
          quality: "High",
          classification: "Management claim",
          knownClaimedInferred: "Claimed",
          references: {
            propositions: ["PROP-REVENUE", "PROP-VALUATION"],
            rikPositions: ["RIK-FINANCIAL", "RIK-RISK"],
          },
        },
        {
          id: "EV-002",
          title: "Signed utility contract summary",
          source: "Mock legal diligence extract",
          sourceType: "Contract evidence",
          date: "2026-07-01",
          extractedFact:
            "Six utility contracts include minimum three-year terms and annual expansion options tied to additional substations.",
          provenance: "Legal extract LEG-07, pages 4-9",
          quality: "High",
          classification: "Verified fact",
          knownClaimedInferred: "Known",
          references: {
            propositions: ["PROP-REVENUE"],
            rikPositions: ["RIK-FINANCIAL", "RIK-GOVERNANCE"],
          },
        },
        {
          id: "EV-003",
          title: "Three utility buyer interviews",
          source: "Mock customer interview notes",
          sourceType: "Primary interview",
          date: "2026-07-02",
          extractedFact:
            "Customers describe Northstar as operationally embedded, but two buyers cite slow workflow integration during deployment.",
          provenance: "Interview packet CUST-03, anonymized notes",
          quality: "Medium",
          classification: "External evidence",
          knownClaimedInferred: "Known",
          references: {
            propositions: ["PROP-MARGINS", "PROP-REGULATORY"],
            rikPositions: ["RIK-MARKET", "RIK-RISK"],
          },
        },
        {
          id: "EV-004",
          title: "State grid modernization budget review",
          source: "Mock regulatory memo",
          sourceType: "External research",
          date: "2026-07-05",
          extractedFact:
            "Two priority states expanded modernization budgets, while one target state delayed procurement approvals by at least one quarter.",
          provenance: "Regulatory memo REG-11, sections 2 and 5",
          quality: "Medium",
          classification: "External evidence",
          knownClaimedInferred: "Known",
          references: {
            propositions: ["PROP-REGULATORY"],
            rikPositions: ["RIK-MARKET", "RIK-RISK"],
          },
        },
        {
          id: "EV-005",
          title: "Series C valuation scenarios",
          source: "Mock finance model",
          sourceType: "Analyst model",
          date: "2026-07-08",
          extractedFact:
            "The 9.5x ARR case requires 30% ARR growth and services gross margin above 55% within four quarters.",
          provenance: "Finance model FIN-22, valuation cases tab",
          quality: "Medium",
          classification: "Analyst inference",
          knownClaimedInferred: "Inferred",
          references: {
            propositions: ["PROP-VALUATION", "PROP-MARGINS"],
            rikPositions: ["RIK-FINANCIAL", "RIK-RISK"],
          },
        },
        {
          id: "EV-006",
          title: "Customer concentration schedule",
          source: "Mock management data room",
          sourceType: "Management data room",
          date: "2026-06-30",
          extractedFact:
            "Top three customers account for 48% of recurring revenue and 61% of services revenue in the reviewed period.",
          provenance: "Data room file MDR-19, concentration schedule",
          quality: "High",
          classification: "Management claim",
          knownClaimedInferred: "Claimed",
          references: {
            propositions: ["PROP-CONCENTRATION", "PROP-REVENUE"],
            rikPositions: ["RIK-FINANCIAL", "RIK-RISK", "RIK-GOVERNANCE"],
          },
        },
        {
          id: "EV-007",
          title: "Implementation cohort margin bridge",
          source: "Mock operations review",
          sourceType: "Internal operating data",
          date: "2026-07-06",
          extractedFact:
            "Deployment margin improved from 38% to 49% across three cohorts, but the newest cohort has not completed stabilization.",
          provenance: "Operations packet OPS-04, margin bridge",
          quality: "Medium",
          classification: "Management claim",
          knownClaimedInferred: "Claimed",
          references: {
            propositions: ["PROP-MARGINS", "PROP-VALUATION"],
            rikPositions: ["RIK-FINANCIAL", "RIK-RISK"],
          },
        },
        {
          id: "EV-008",
          title: "Board reporting sample",
          source: "Mock governance diligence",
          sourceType: "Governance artifact",
          date: "2026-07-09",
          extractedFact:
            "Monthly financial reporting is consistent, but cyber-risk and deployment-risk reporting are not standardized for board review.",
          provenance: "Governance packet GOV-02",
          quality: "Medium",
          classification: "Verified fact",
          knownClaimedInferred: "Known",
          references: {
            propositions: ["PROP-GOVERNANCE", "PROP-CONCENTRATION"],
            rikPositions: ["RIK-GOVERNANCE", "RIK-RISK"],
          },
        },
        {
          id: "EV-009",
          title: "Unverified enterprise expansion pipeline",
          source: "Mock management pipeline review",
          sourceType: "Management forecast",
          date: "2026-07-10",
          extractedFact:
            "Management claims two non-utility enterprise prospects could close before Series D, but no signed LOIs were provided.",
          provenance: "Pipeline review PIPE-06",
          quality: "Low",
          classification: "Missing or unresolved",
          knownClaimedInferred: "Missing",
          references: {
            propositions: ["PROP-CONCENTRATION"],
            rikPositions: ["RIK-MARKET", "RIK-RISK"],
          },
        },
      ],
      rikPositions: [
        {
          id: "RIK-MARKET",
          name: "Market RIK",
          domain: "Market demand and adoption",
          status: "Complete",
          confidence: "Moderate",
          primaryConclusion:
            "Market demand is real and durable enough to justify continued diligence, but procurement timing should be treated as a live uncertainty.",
          decisiveEvidence: ["EV-003", "EV-004", "EV-009"],
          assumptions: [
            "Grid modernization budgets remain allocated across Northstar's core states.",
            "Customer interview sentiment is representative of broader utility buyer needs.",
          ],
          strongestObjection:
            "Utility procurement cycles may stretch beyond the investment model's timing assumptions.",
          changeEvidence:
            "Procurement deferrals in two additional states or failed enterprise pipeline conversion would weaken the position.",
          relatedPropositions: ["PROP-REGULATORY", "PROP-CONCENTRATION"],
        },
        {
          id: "RIK-FINANCIAL",
          name: "Financial RIK",
          domain: "Revenue quality, margin path, and valuation",
          status: "Complete",
          confidence: "Moderate",
          primaryConclusion:
            "Revenue durability supports investment, but valuation should be conditioned by concentration and implementation-margin evidence.",
          decisiveEvidence: ["EV-001", "EV-002", "EV-005", "EV-006", "EV-007"],
          assumptions: [
            "Management ARR schedules are directionally accurate pending final audit.",
            "Services margin improvement continues as deployment playbooks mature.",
          ],
          strongestObjection:
            "Top-customer concentration and services intensity make a premium ARR multiple difficult to justify today.",
          changeEvidence:
            "Audited retention data, lower concentration, or sustained services margin above 55% would support a stronger valuation stance.",
          relatedPropositions: [
            "PROP-REVENUE",
            "PROP-VALUATION",
            "PROP-MARGINS",
            "PROP-CONCENTRATION",
          ],
        },
        {
          id: "RIK-RISK",
          name: "Risk RIK",
          domain: "Downside cases and fragility",
          status: "Complete",
          confidence: "High",
          primaryConclusion:
            "The investment can proceed only if concentration, regulatory timing, and deployment execution are converted into explicit conditions.",
          decisiveEvidence: ["EV-003", "EV-004", "EV-005", "EV-006", "EV-007", "EV-009"],
          assumptions: [
            "Management pipeline claims should not be treated as de-risking evidence without signed commitments.",
            "Implementation services remain a constraint until cohort stabilization is observed.",
          ],
          strongestObjection:
            "The downside case may be overly conservative if the pipeline converts quickly after the investment.",
          changeEvidence:
            "Signed enterprise commitments, documented procurement acceleration, or stabilized cohort margins would reduce the risk objection.",
          relatedPropositions: [
            "PROP-VALUATION",
            "PROP-REGULATORY",
            "PROP-MARGINS",
            "PROP-CONCENTRATION",
          ],
        },
        {
          id: "RIK-GOVERNANCE",
          name: "Governance RIK",
          domain: "Controls, information rights, and decision conditions",
          status: "Complete",
          confidence: "Moderate",
          primaryConclusion:
            "Governance is investable only if the committee secures reporting rights, board observation, and concentration monitoring.",
          decisiveEvidence: ["EV-002", "EV-006", "EV-008"],
          assumptions: [
            "Management will accept investor reporting conditions as part of the Series C.",
            "Board observer rights are available without delaying the financing.",
          ],
          strongestObjection:
            "Governance conditions may not fully mitigate operating risks if management lacks reporting discipline.",
          changeEvidence:
            "A board-approved reporting calendar and cyber-risk dashboard would improve the position.",
          relatedPropositions: ["PROP-GOVERNANCE", "PROP-CONCENTRATION", "PROP-REVENUE"],
        },
      ],
      contestedPropositions: [
        {
          id: "PROP-VALUATION",
          theme: "Valuation",
          proposition:
            "A valuation of 9.5x ARR is justified by Northstar's revenue quality.",
          status: "Decision overridden",
          summary:
            "Revenue quality supports a growth valuation, but the institutional decision rejects the full 9.5x case and uses a conditioned base case.",
          positions: [
            {
              rikId: "RIK-FINANCIAL",
              stance: "SUPPORTS",
              confidence: "Moderate",
              reasoning:
                "Retention, signed contracts, and recurring expansion rights support a premium to typical services-heavy software companies.",
              assumptions: [
                "ARR schedule is materially accurate.",
                "Margin improvement continues over the next four quarters.",
              ],
              evidence: ["EV-001", "EV-002", "EV-005"],
              changePosition:
                "Failed ARR audit or stalled deployment margins would remove support for the 9.5x case.",
            },
            {
              rikId: "RIK-RISK",
              stance: "OPPOSES",
              confidence: "High",
              reasoning:
                "The 9.5x case underprices customer concentration and depends on unproven services-margin expansion.",
              assumptions: [
                "Top-customer concentration remains economically material.",
                "Pipeline claims should not be priced as closed diversification.",
              ],
              evidence: ["EV-005", "EV-006", "EV-007", "EV-009"],
              changePosition:
                "Signed diversification evidence or sustained cohort margins above 55% would reduce opposition.",
            },
            {
              rikId: "RIK-MARKET",
              stance: "CONDITIONAL",
              confidence: "Moderate",
              reasoning:
                "Demand quality is strong, but valuation depends on procurement timing and market expansion beyond core utilities.",
              assumptions: [
                "Budget tailwinds remain available.",
                "Enterprise pipeline can diversify revenue before Series D.",
              ],
              evidence: ["EV-003", "EV-004", "EV-009"],
              changePosition:
                "Procurement delays or failed enterprise expansion would move the position toward oppose.",
            },
          ],
        },
        {
          id: "PROP-REGULATORY",
          theme: "Regulatory timing",
          proposition:
            "Regulatory and budget timing support Northstar's near-term growth plan.",
          status: "Partially resolved",
          summary:
            "Budget support is visible, but procurement timing remains uncertain enough to require downside-case planning.",
          positions: [
            {
              rikId: "RIK-MARKET",
              stance: "SUPPORTS",
              confidence: "Moderate",
              reasoning:
                "Modernization budgets and customer interviews indicate continued demand for grid orchestration software.",
              assumptions: [
                "Budget allocations translate into procurement activity within the modeled period.",
              ],
              evidence: ["EV-003", "EV-004"],
              changePosition:
                "Two-quarter procurement slippage across core states would weaken this support.",
            },
            {
              rikId: "RIK-RISK",
              stance: "CONDITIONAL",
              confidence: "High",
              reasoning:
                "One target state has already delayed approvals, so the decision should not depend on the fastest timing case.",
              assumptions: [
                "Regulatory delay is a repeatable risk rather than a one-off event.",
              ],
              evidence: ["EV-004"],
              changePosition:
                "Confirmed procurement awards in the delayed state would reduce the condition.",
            },
          ],
        },
        {
          id: "PROP-MARGINS",
          theme: "Implementation margins",
          proposition:
            "Implementation margins are improving fast enough to support enterprise software economics.",
          status: "Unresolved",
          summary:
            "The data shows improvement, but the newest cohort has not stabilized and the evidence does not justify a clean consensus.",
          positions: [
            {
              rikId: "RIK-FINANCIAL",
              stance: "CONDITIONAL",
              confidence: "Moderate",
              reasoning:
                "Cohort improvement is promising, but enterprise software economics require proof that services intensity declines.",
              assumptions: [
                "Deployment playbooks can be repeated across new accounts.",
              ],
              evidence: ["EV-005", "EV-007"],
              changePosition:
                "Two additional stabilized cohorts above 55% services margin would strengthen support.",
            },
            {
              rikId: "RIK-RISK",
              stance: "OPPOSES",
              confidence: "Moderate",
              reasoning:
                "The newest cohort has not stabilized, so margin claims remain incomplete for valuation purposes.",
              assumptions: [
                "Unstabilized cohorts should not be counted as proof of operating leverage.",
              ],
              evidence: ["EV-003", "EV-007"],
              changePosition:
                "Verified cohort stabilization and lower onboarding support hours would reduce opposition.",
            },
          ],
        },
        {
          id: "PROP-CONCENTRATION",
          theme: "Customer concentration",
          proposition:
            "Customer concentration risk is acceptable for a growth-stage investment.",
          status: "Partially resolved",
          summary:
            "Concentration remains material, but the decision can proceed if it is converted into a governance and reporting condition.",
          positions: [
            {
              rikId: "RIK-FINANCIAL",
              stance: "CONDITIONAL",
              confidence: "Moderate",
              reasoning:
                "Concentration is high, but contract duration and retention evidence make it manageable with explicit monitoring.",
              assumptions: [
                "Large customers remain satisfied through the next deployment cycle.",
              ],
              evidence: ["EV-001", "EV-002", "EV-006"],
              changePosition:
                "Renewal risk in any top-three customer would move the position toward oppose.",
            },
            {
              rikId: "RIK-RISK",
              stance: "OPPOSES",
              confidence: "High",
              reasoning:
                "Top-three ARR concentration is too high to treat as ordinary growth-stage risk without signed diversification evidence.",
              assumptions: [
                "Pipeline claims should not reduce concentration risk until signed.",
              ],
              evidence: ["EV-006", "EV-009"],
              changePosition:
                "Signed enterprise contracts or top-three ARR below 35% would reduce opposition.",
            },
            {
              rikId: "RIK-GOVERNANCE",
              stance: "CONDITIONAL",
              confidence: "Moderate",
              reasoning:
                "Investor information rights can make the risk monitorable, but cannot eliminate the underlying exposure.",
              assumptions: [
                "Management accepts concentration reporting and board oversight.",
              ],
              evidence: ["EV-006", "EV-008"],
              changePosition:
                "Refusal of reporting rights would move the governance position to oppose.",
            },
          ],
        },
        {
          id: "PROP-GOVERNANCE",
          theme: "Governance readiness",
          proposition:
            "Northstar can support institutional-grade investor oversight after the Series C.",
          status: "Resolved",
          summary:
            "Governance is adequate only with added reporting obligations and board observation rights.",
          positions: [
            {
              rikId: "RIK-GOVERNANCE",
              stance: "CONDITIONAL",
              confidence: "Moderate",
              reasoning:
                "Financial reporting is consistent, but risk reporting requires a defined board package.",
              assumptions: [
                "The Series C gives investors enough leverage to secure reporting terms.",
              ],
              evidence: ["EV-008", "EV-002"],
              changePosition:
                "A board-approved risk dashboard would convert the position from conditional to support.",
            },
            {
              rikId: "RIK-RISK",
              stance: "CONDITIONAL",
              confidence: "Moderate",
              reasoning:
                "Oversight terms reduce but do not remove execution risk.",
              assumptions: [
                "Reporting visibility allows earlier intervention if execution deteriorates.",
              ],
              evidence: ["EV-008"],
              changePosition:
                "Weak reporting compliance after closing would increase opposition.",
            },
          ],
        },
        {
          id: "PROP-REVENUE",
          theme: "Revenue durability",
          proposition:
            "Northstar's revenue durability is sufficient for a growth-stage investment.",
          status: "Partially resolved",
          summary:
            "Contract duration and retention support durability, but concentration limits how strongly the proposition can be accepted.",
          positions: [
            {
              rikId: "RIK-FINANCIAL",
              stance: "SUPPORTS",
              confidence: "High",
              reasoning:
                "Signed multi-year terms and strong cohort retention support durable revenue.",
              assumptions: [
                "ARR data survives final audit without material restatement.",
              ],
              evidence: ["EV-001", "EV-002"],
              changePosition:
                "Material ARR restatement or contract termination rights would weaken support.",
            },
            {
              rikId: "RIK-GOVERNANCE",
              stance: "CONDITIONAL",
              confidence: "Moderate",
              reasoning:
                "Revenue can support the decision only if concentration is made transparent to investors.",
              assumptions: [
                "Management accepts reporting requirements.",
              ],
              evidence: ["EV-002", "EV-006", "EV-008"],
              changePosition:
                "No reporting covenant would weaken the governance position.",
            },
          ],
        },
      ],
      decisionLedger: [
        {
          id: "DEC-REVENUE",
          title: "Revenue durability",
          proposition:
            "Northstar's revenue durability is sufficient for a growth-stage investment.",
          institutionalPosition: "ACCEPTS WITH CONDITIONS",
          decisionStrength: "Moderate",
          reason:
            "Contracted revenue and retention support durability, but customer concentration remains material.",
          conflictId: "PROP-REVENUE",
          rikPositions: ["RIK-FINANCIAL", "RIK-GOVERNANCE"],
          decisiveEvidence: ["EV-001", "EV-002", "EV-006"],
          remainingUncertainty:
            "Management ARR schedules still need final audit confirmation and concentration monitoring.",
          conditionId: "COND-CONCENTRATION",
        },
        {
          id: "DEC-VALUATION",
          title: "Valuation discipline",
          proposition:
            "A valuation of 9.5x ARR is justified by Northstar's revenue quality.",
          institutionalPosition: "REJECTS",
          decisionStrength: "Moderate",
          reason:
            "The full 9.5x case depends on unresolved margin and concentration assumptions.",
          conflictId: "PROP-VALUATION",
          rikPositions: ["RIK-FINANCIAL", "RIK-RISK", "RIK-MARKET"],
          decisiveEvidence: ["EV-005", "EV-006", "EV-007", "EV-009"],
          remainingUncertainty:
            "The correct valuation may move upward if diversification and cohort margins improve.",
          conditionId: "COND-FOLLOW-ON",
        },
        {
          id: "DEC-REGULATORY",
          title: "Regulatory timing",
          proposition:
            "Regulatory and budget timing support Northstar's near-term growth plan.",
          institutionalPosition: "ACCEPTS WITH CONDITIONS",
          decisionStrength: "Moderate",
          reason:
            "Budget support is visible, but procurement delay risk requires a downside case.",
          conflictId: "PROP-REGULATORY",
          rikPositions: ["RIK-MARKET", "RIK-RISK"],
          decisiveEvidence: ["EV-003", "EV-004"],
          remainingUncertainty:
            "The delayed target state may not return to the modeled timeline.",
          conditionId: "COND-DOWNSIDE",
        },
        {
          id: "DEC-MARGINS",
          title: "Implementation economics",
          proposition:
            "Implementation margins are improving fast enough to support enterprise software economics.",
          institutionalPosition: "LEAVES UNRESOLVED",
          decisionStrength: "Contested",
          reason:
            "The evidence shows improvement but not enough stabilized cohort data for a final conclusion.",
          conflictId: "PROP-MARGINS",
          rikPositions: ["RIK-FINANCIAL", "RIK-RISK"],
          decisiveEvidence: ["EV-003", "EV-005", "EV-007"],
          remainingUncertainty:
            "The newest deployment cohort has not completed stabilization.",
          conditionId: "COND-MARGIN",
        },
        {
          id: "DEC-GOVERNANCE",
          title: "Governance package",
          proposition:
            "Northstar can support institutional-grade investor oversight after the Series C.",
          institutionalPosition: "ACCEPTS WITH CONDITIONS",
          decisionStrength: "Moderate",
          reason:
            "The company has baseline reporting discipline, but investor oversight needs to be formalized.",
          conflictId: "PROP-GOVERNANCE",
          rikPositions: ["RIK-GOVERNANCE", "RIK-RISK"],
          decisiveEvidence: ["EV-002", "EV-008"],
          remainingUncertainty:
            "Board-level risk reporting quality remains unproven.",
          conditionId: "COND-GOVERNANCE",
        },
      ],
      investmentConditions: [
        {
          id: "COND-CONCENTRATION",
          text: "Quarterly concentration reporting with a defined path below 35% top-three ARR.",
          sourceDecision: "DEC-REVENUE",
        },
        {
          id: "COND-FOLLOW-ON",
          text: "Use an 8.0x ARR base case and reserve follow-on rights tied to revenue diversification.",
          sourceDecision: "DEC-VALUATION",
        },
        {
          id: "COND-DOWNSIDE",
          text: "Investment memo must include a downside case with a two-quarter procurement delay.",
          sourceDecision: "DEC-REGULATORY",
        },
        {
          id: "COND-MARGIN",
          text: "Management must deliver quarterly cohort-margin reporting for implementation services.",
          sourceDecision: "DEC-MARGINS",
        },
        {
          id: "COND-GOVERNANCE",
          text: "Board observer right and risk-reporting package required before funding closes.",
          sourceDecision: "DEC-GOVERNANCE",
        },
      ],
      unresolvedQuestions: [
        {
          id: "UQ-001",
          question:
            "Can Northstar secure two non-utility enterprise customers before the next financing?",
          relatedEvidence: ["EV-009"],
          relatedPropositions: ["PROP-CONCENTRATION"],
          severity: "Medium",
        },
        {
          id: "UQ-002",
          question:
            "Will implementation gross margin exceed 55% for two stabilized deployment cohorts?",
          relatedEvidence: ["EV-007"],
          relatedPropositions: ["PROP-MARGINS", "PROP-VALUATION"],
          severity: "High",
        },
        {
          id: "UQ-003",
          question:
            "Can management provide board-ready cyber-risk reporting within 60 days?",
          relatedEvidence: ["EV-008"],
          relatedPropositions: ["PROP-GOVERNANCE"],
          severity: "Medium",
        },
      ],
      decision: {
        outcome: "Approve with conditions",
        decisionStrength: "Moderate",
        rationale:
          "The institutional decision accepts revenue durability and market demand with conditions, rejects the full premium valuation case, and leaves implementation economics unresolved until further evidence is produced.",
        ledgerEntries: [
          "DEC-REVENUE",
          "DEC-VALUATION",
          "DEC-REGULATORY",
          "DEC-MARGINS",
          "DEC-GOVERNANCE",
        ],
      },
    },
  ],
  blankCaseDefaults: {
    title: "Untitled investment case",
    company: "New company",
    ticker: "TBD",
    sector: "TBD",
    geography: "TBD",
    sponsor: "YUKTI Investment Committee",
    owner: "Current user",
    stage: "Intake draft",
    requestedDecision: "TBD",
    investmentType: "TBD",
    timeHorizon: "TBD",
    mandateFit: "Not yet assessed",
    investmentThesis:
      "Draft case created in the prototype UI. No fixture analysis is attached to user-created cases.",
    reasoningModel:
      "No institutional reasoning graph exists for this draft case.",
    keyQuestions: [
      "What decision is the committee being asked to make?",
      "Which evidence should be reviewed before analysis begins?",
      "Which risks would block approval?",
    ],
  },
};
