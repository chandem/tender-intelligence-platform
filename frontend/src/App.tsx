import { useState } from "react";

const API = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

export default function App() {
  const [page, setPage] = useState("Dashboard");
  const [health, setHealth] = useState("Not checked");
  const checkApi = async () => { try { const r = await fetch(API + "/health"); setHealth(r.ok ? "API online" : "API error"); } catch { setHealth("API unreachable"); } };
  return <div className="app"><aside><h1>TenderIQ</h1><p className="muted">Tender Intelligence Platform</p>{["Dashboard","Tenders","Contractor Profile","Matches"].map(x=><button className={page===x?"nav active":"nav"} onClick={()=>setPage(x)} key={x}>{x}</button>)}<div className="side-bottom"><button onClick={checkApi}>Check API</button><span>{health}</span></div></aside><main><header><div><p className="eyebrow">Tender Intelligence</p><h2>{page}</h2></div><button className="primary">+ New Tender</button></header>{page==="Dashboard"?<Dashboard/>:<section className="card"><h3>{page}</h3><p className="muted">This module is connected to the backend foundation and will be expanded next.</p></section>}</main></div>
}
function Dashboard(){return <><div className="hero"><div><h3>Know your tenders before you bid.</h3><p>Upload tender documents, extract requirements with AI, and compare them with your contractor profile.</p></div><button className="primary">Upload Tender PDF</button></div><div className="grid">{[["0","New Tenders"],["0","Processing"],["0","Analyzed"],["0","Potential Matches"]].map(([n,l])=><div className="stat card" key={l}><strong>{n}</strong><span>{l}</span></div>)}</div><section className="card"><h3>Recent tenders</h3><p className="muted">No tenders yet. Create your first tender to begin the intelligence workflow.</p></section></>}
