// ProfsAgent graph schema — DRAFT v0.1 (not frozen; see docs/01_stage1_architecture.md §4, §5)
// Target: Neo4j 5.x Community. Only uniqueness constraints and (range / text / vector) indexes are used,
// because node-key and existence constraints are Enterprise-only. Required properties are enforced in
// Pydantic before any write and re-checked by validator V22.

// ─────────────────────────── LAYER A — Institutional graph ───────────────────────────
CREATE CONSTRAINT institution_uid IF NOT EXISTS FOR (n:Institution)        REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT programme_uid   IF NOT EXISTS FOR (n:Programme)          REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT peo_uid         IF NOT EXISTS FOR (n:PEO)                REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT po_uid          IF NOT EXISTS FOR (n:PO)                 REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT course_uid      IF NOT EXISTS FOR (n:Course)             REQUIRE n.uid IS UNIQUE;   // primary code, e.g. "CSE201"
CREATE CONSTRAINT corpus_co_uid   IF NOT EXISTS FOR (n:CourseOutcome)      REQUIRE n.uid IS UNIQUE;   // "CSE201/CO3"
CREATE CONSTRAINT weekplan_uid    IF NOT EXISTS FOR (n:WeekPlan)           REQUIRE n.uid IS UNIQUE;   // "CSE201/W06"
CREATE CONSTRAINT labplan_uid     IF NOT EXISTS FOR (n:LabPlan)            REQUIRE n.uid IS UNIQUE;   // "CSE201/L06"
CREATE CONSTRAINT topic_uid       IF NOT EXISTS FOR (n:Topic)              REQUIRE n.uid IS UNIQUE;   // "T:object-oriented-design"
CREATE CONSTRAINT mention_uid     IF NOT EXISTS FOR (n:TopicMention)       REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT event_uid       IF NOT EXISTS FOR (n:CourseEvent)        REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT acomp_uid       IF NOT EXISTS FOR (n:AssessmentComponent) REQUIRE n.uid IS UNIQUE;  // "CSE201/A:Quiz"
CREATE CONSTRAINT resource_uid    IF NOT EXISTS FOR (n:Resource)           REQUIRE n.uid IS UNIQUE;   // "R:isbn:…", "R:doi:…", "R:hash:…"
CREATE CONSTRAINT faculty_uid     IF NOT EXISTS FOR (n:Faculty)            REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT source_uid      IF NOT EXISTS FOR (n:SourceDoc)          REQUIRE n.uid IS UNIQUE;   // "SRC:<sha256[:12]>"
CREATE CONSTRAINT extcourse_uid   IF NOT EXISTS FOR (n:ExternalCourse)     REQUIRE n.uid IS UNIQUE;   // "EXT:<host>/<slug>"

CREATE INDEX course_level   IF NOT EXISTS FOR (n:Course) ON (n.level);
CREATE INDEX course_cluster IF NOT EXISTS FOR (n:Course) ON (n.cluster);
CREATE INDEX co_quality     IF NOT EXISTS FOR (n:CourseOutcome) ON (n.quality_score);
CREATE INDEX co_bloom       IF NOT EXISTS FOR (n:CourseOutcome) ON (n.bloom_lexicon);
CREATE INDEX topic_backbone IF NOT EXISTS FOR (n:Topic) ON (n.backbone_ref);
CREATE FULLTEXT INDEX course_text IF NOT EXISTS FOR (n:Course) ON EACH [n.name, n.description];
CREATE FULLTEXT INDEX topic_text  IF NOT EXISTS FOR (n:Topic)  ON EACH [n.canonical_name, n.definition];

// Vector indexes (Neo4j ≥ 5.13). Set dimensions to the chosen embedding model (BGE-M3 = 1024).
CREATE VECTOR INDEX topic_vec IF NOT EXISTS FOR (n:Topic) ON (n.embedding)
  OPTIONS { indexConfig: { `vector.dimensions`: 1024, `vector.similarity_function`: 'cosine' } };
CREATE VECTOR INDEX course_vec IF NOT EXISTS FOR (n:Course) ON (n.embedding)
  OPTIONS { indexConfig: { `vector.dimensions`: 1024, `vector.similarity_function`: 'cosine' } };
CREATE VECTOR INDEX corpus_co_vec IF NOT EXISTS FOR (n:CourseOutcome) ON (n.embedding)
  OPTIONS { indexConfig: { `vector.dimensions`: 1024, `vector.similarity_function`: 'cosine' } };

// Relationship vocabulary, Layer A (documentation only — Neo4j has no relationship schema):
// (Programme)-[:HAS_PEO]->(PEO)            (Programme)-[:HAS_PO]->(PO)          (PO)-[:SERVES]->(PEO)
// (Programme)-[:CORE|ELECTIVE]->(Course)
// (Course)-[:REQUIRES {kind, raw, confidence}]->(Course)
// (Course)-[:REQUIRES_SKILL {kind, raw}]->(Topic)
// (Course)-[:ANTI_REQUISITE {raw}]->(Course)
// (Course)-[:HAS_CO]->(CourseOutcome)
// (Course)-[:HAS_WEEK]->(WeekPlan)-[:COVERS {order}]->(Topic)
// (WeekPlan)-[:MEETS]->(CourseOutcome)     (WeekPlan)-[:HAS_EVENT]->(CourseEvent)
// (WeekPlan)-[:HAS_MENTION]->(TopicMention)-[:CANONICAL]->(Topic)
// (Course)-[:HAS_LAB]->(LabPlan)-[:COVERS]->(Topic)
// (Course)-[:HAS_ASSESSMENT]->(AssessmentComponent)
// (Course)-[:USES_RESOURCE {type}]->(Resource)
// (Course)-[:TAUGHT_BY {semester}]->(Faculty)
// (Topic)-[:BROADER_THAN]->(Topic)
// (Topic)-[:PRECEDES {support, courses, method}]->(Topic)
// (CourseOutcome)-[:ADDRESSES {via_weeks}]->(Topic)
// (CourseOutcome)-[:MAPS_TO_INFERRED {relevance, justification, model, prompt_id}]->(PO)
// (Course)-[:OVERLAPS {weighted_jaccard, shared_topics}]->(Course)
// (*)-[:DERIVED_FROM {cells, char_span}]->(SourceDoc)

// ─────────────────────────── LAYER B — Course design graph ───────────────────────────
// Every Layer-B node: uid = "<project_id>/<local_id>", plus project_id, local_id, version, status,
// created_by, run_id, prompt_id, prompt_version, model, sources.
CREATE CONSTRAINT project_uid    IF NOT EXISTS FOR (n:DesignProject)  REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT newcourse_uid  IF NOT EXISTS FOR (n:NewCourse)      REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT ctxfield_uid   IF NOT EXISTS FOR (n:ContextField)   REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT constraint_uid IF NOT EXISTS FOR (n:Constraint)     REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT assumption_uid IF NOT EXISTS FOR (n:Assumption)     REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT tgroup_uid     IF NOT EXISTS FOR (n:TopicGroup)     REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT co_uid         IF NOT EXISTS FOR (n:CO)             REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT lo_uid         IF NOT EXISTS FOR (n:LO)             REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT module_uid     IF NOT EXISTS FOR (n:Module)         REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT ctopic_uid     IF NOT EXISTS FOR (n:CourseTopic)    REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT week_uid       IF NOT EXISTS FOR (n:Week)           REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT lecture_uid    IF NOT EXISTS FOR (n:Lecture)        REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT lab_uid        IF NOT EXISTS FOR (n:LabSession)     REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT tut_uid        IF NOT EXISTS FOR (n:Tutorial)       REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT assess_uid     IF NOT EXISTS FOR (n:Assessment)     REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT aitem_uid      IF NOT EXISTS FOR (n:AssessmentItem) REQUIRE n.uid IS UNIQUE;   // Stage 2+
CREATE CONSTRAINT rubric_uid     IF NOT EXISTS FOR (n:Rubric)         REQUIRE n.uid IS UNIQUE;   // Stage 2+
CREATE CONSTRAINT material_uid   IF NOT EXISTS FOR (n:Material)       REQUIRE n.uid IS UNIQUE;   // Stage 2+
CREATE CONSTRAINT approval_uid   IF NOT EXISTS FOR (n:Approval)       REQUIRE n.uid IS UNIQUE;
CREATE CONSTRAINT violation_uid  IF NOT EXISTS FOR (n:Violation)      REQUIRE n.uid IS UNIQUE;

CREATE INDEX lb_project_co    IF NOT EXISTS FOR (n:CO)          ON (n.project_id, n.status);
CREATE INDEX lb_project_lo    IF NOT EXISTS FOR (n:LO)          ON (n.project_id, n.status);
CREATE INDEX lb_project_topic IF NOT EXISTS FOR (n:CourseTopic) ON (n.project_id, n.status);
CREATE INDEX lb_project_asmt  IF NOT EXISTS FOR (n:Assessment)  ON (n.project_id, n.status);
CREATE INDEX lb_week_n        IF NOT EXISTS FOR (n:Week)        ON (n.project_id, n.n);
CREATE INDEX lb_violation     IF NOT EXISTS FOR (n:Violation)   ON (n.project_id, n.code, n.resolved);

// Relationship vocabulary, Layer B:
// (DesignProject)-[:DESIGNS]->(NewCourse)
// (NewCourse)-[:HAS_CONTEXT]->(ContextField)   (NewCourse)-[:HAS_CONSTRAINT]->(Constraint)
// (NewCourse)-[:HAS_ASSUMPTION]->(Assumption)  (NewCourse)-[:HAS_TOPIC_GROUP]->(TopicGroup)
// (NewCourse)-[:HAS_CO]->(CO)-[:DECOMPOSES_INTO]->(LO)
// (CO)-[:MAPS_TO {relevance, strength_provisional, strength_computed, justification}]->(PO)     // PO is Layer A
// (CO)-[:COVERS_GROUP]->(TopicGroup)
// (LO)-[:REQUIRES]->(LO)
// (LO)-[:TAUGHT_VIA]->(CourseTopic)
// (NewCourse)-[:HAS_MODULE]->(Module)-[:CONTAINS {order}]->(CourseTopic)
// (CourseTopic)-[:REQUIRES {reason}]->(CourseTopic)
// (CourseTopic)-[:SAME_AS {sim}]->(Topic)                                                         // Layer A
// (CourseTopic)-[:DELIVERED_IN {hours}]->(Lecture)-[:IN_WEEK]->(Week)
// (LO)-[:PRACTISED_IN]->(LabSession|Tutorial)-[:IN_WEEK]->(Week)
// (Assessment)-[:ASSESSES {marks_pct, bloom_level}]->(LO)
// (Assessment)-[:COVERS]->(CourseTopic)
// (Assessment)-[:RELEASED_IN]->(Week)   (Assessment)-[:DUE_IN]->(Week)
// (Assessment)-[:CONTAINS]->(AssessmentItem)-[:TARGETS]->(LO)                                   // Stage 2+
// (AssessmentItem)-[:EVALUATED_WITH]->(Rubric)                                                  // Stage 2+
// (Lecture)-[:USES]->(Material)                                                                 // Stage 2+
// (CourseTopic)-[:READING]->(Resource)
// (NewCourse)-[:REQUIRES {kind, justification, relied_topics}]->(Course)
// (NewCourse)-[:OVERLAPS {weighted_jaccard, shared_topics, verdict}]->(Course)
// (NewCourse)-[:COMPARABLE_TO {what_taken}]->(Course|ExternalCourse)
// (*)-[:GROUNDED_IN {span}]->(Layer A node | SourceDoc)
// (Approval)-[:FREEZES]->(*)          (new)-[:SUPERSEDES]->(old)
// (Violation)-[:ON]->(*)

// ─────────────────────────── Sample validator queries ───────────────────────────
// V9 / T6 — LOs never assessed at or above their Bloom level:
//   MATCH (lo:LO {project_id:$p}) WHERE lo.status <> 'superseded'
//   AND NOT EXISTS { MATCH (a:Assessment)-[r:ASSESSES]->(lo) WHERE r.bloom_level >= lo.bloom_level }
//   RETURN lo.uid;
// V19 / T7 — assessment covers a topic taught after its release week:
//   MATCH (a:Assessment {project_id:$p})-[:RELEASED_IN]->(rw:Week),
//         (a)-[:COVERS]->(t:CourseTopic)-[:DELIVERED_IN]->(:Lecture)-[:IN_WEEK]->(tw:Week)
//   WHERE tw.n > rw.n RETURN a.uid, t.uid, tw.n AS taught, rw.n AS released;
// T2 — CO has no LO at its own Bloom level:
//   MATCH (co:CO {project_id:$p}) WHERE NOT EXISTS {
//     MATCH (co)-[:DECOMPOSES_INTO]->(lo:LO) WHERE lo.bloom_level = co.bloom_level } RETURN co.uid;
// V24 — gold leakage:
//   MATCH (c:Course {is_gold_stub:true})
//   WHERE EXISTS { (c)-[:HAS_CO|HAS_WEEK|HAS_LAB|HAS_ASSESSMENT|USES_RESOURCE]->() } OR c.embedding IS NOT NULL
//   RETURN c.uid;
