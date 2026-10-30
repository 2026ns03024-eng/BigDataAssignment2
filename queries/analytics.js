// MongoDB aggregation demos for Assignment 2 Scenario 3 (run in mongosh).
// Usage: mongosh "mongodb://HOST:PORT/readmission" --file queries/analytics.js

const dbName = db.getName();

print("\n=== 1) $lookup: encounters with patient demographics (sample 5) ===");
db.encounters.aggregate([
  { $lookup: {
      from: "patients",
      localField: "patient_nbr",
      foreignField: "patient_nbr",
      as: "patient",
  }},
  { $unwind: "$patient" },
  { $project: {
      encounter_id: 1,
      readmitted: 1,
      time_in_hospital: 1,
      race: "$patient.race",
      gender: "$patient.gender",
      age: "$patient.age",
  }},
  { $limit: 5 },
]).forEach(doc => printjson(doc));

print("\n=== 2) $graphLookup: prior stays for one patient chain (limit 3 roots) ===");
db.encounters.aggregate([
  { $match: { prev_encounter_id: { $ne: null } } },
  { $limit: 3 },
  { $graphLookup: {
      from: "encounters",
      startWith: "$prev_encounter_id",
      connectFromField: "prev_encounter_id",
      connectToField: "encounter_id",
      as: "prior_stays",
      maxDepth: 5,
  }},
  { $project: {
      encounter_id: 1,
      prev_encounter_id: 1,
      prior_count: { $size: "$prior_stays" },
  }},
]).forEach(doc => printjson(doc));

print("\n=== 3) $setWindowFields: rolling mean heart rate within encounter (one encounter) ===");
const sampleEnc = db.encounters.findOne({}, { encounter_id: 1 });
const eid = sampleEnc.encounter_id;
db.vitals.aggregate([
  { $match: { encounter_id: eid } },
  { $sort: { ts: 1 } },
  { $setWindowFields: {
      partitionBy: "$encounter_id",
      sortBy: { ts: 1 },
      output: {
        rolling_hr_mean: {
          $avg: "$heart_rate_bpm",
          window: { documents: [-2, 0] },
        },
      },
  }},
]).forEach(doc => printjson(doc));

print("\n=== 4) $bucket: length of stay vs 30-day readmission rate ===");
db.encounters.aggregate([
  { $addFields: {
      readmit_flag: { $cond: [{ $eq: ["$readmitted", "<30"] }, 1, 0] },
  }},
  { $bucket: {
      groupBy: "$time_in_hospital",
      boundaries: [1, 4, 8, 12, 16],
      default: "16+",
      output: {
        encounters: { $sum: 1 },
        readmit_30d: { $sum: "$readmit_flag" },
      },
  }},
  { $addFields: {
      readmit_rate: {
        $round: [{ $divide: ["$readmit_30d", "$encounters"] }, 4],
      },
  }},
  { $sort: { _id: 1 } },
]).forEach(doc => printjson(doc));

print("\nDone.");
