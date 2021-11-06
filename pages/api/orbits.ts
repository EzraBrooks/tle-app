// Next.js API route support: https://nextjs.org/docs/api-routes/introduction
import { MongoClient } from "mongodb";
import type { NextApiRequest, NextApiResponse } from "next";

const uri = "mongodb://localhost:27017/orbits";
const client = new MongoClient(uri);

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  await client.connect();
  const database = client.db();
  const collection = database.collection("czml");
  res.status(200).json(
    await collection
      .aggregate([
        {
          $match: {
            id: { $regex: "^((?!deb)(?!r/b).)*$", $options: "i" },
          },
        },
      ])
      .limit(100)
      .toArray()
  );
}
