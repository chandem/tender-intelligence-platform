import { useEffect, useState } from "react";
import { api, API_BASE, type Tender } from "./api";
import { supabase } from "./auth";

export default function App() {
  const [session, setSession] = useState<any>(null);
  const [page, setPage] = useState("Dashboard");
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [title, setTitle] = useState("");
  const [organization, setOrganization] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [health, setHealth] = useState("Not checked");

  useEffect(() => {
    supabase.auth.getSession().then(({data}) => setSession(data.session));
    const {data:{subscription}} = supabase.auth.onAuthStateChange((_event, s) => {
      setSession(s);
      if (s?.access_token) localStorage.setItem("tenderiq_token", s.access_token);
      else localStorage.removeItem("tenderiq_token");
    });
    return () => subscription.unsubscribe();
  }, []);

  const loadTenders = async () => {
    if (!session) return;
    try { setTenders(await api<Tender[]>("/tenders")); } catch { setTenders([]); }
  };
  useEffect(() => { loadTenders(); }, [session]);

  const signIn = async () => {
    setMessage("");
    const {error} = await supabase.auth.signInWithPassword({email, password});
    if (error) setMessage(error.message);
  };
  const signUp = async () => {
    setMessage("");
    const {error} = await supabase.auth.signUp({email, password});
    if (error) setMessage(error.message);
    else setMessage("Account created. Check your email if confirmation is enabled.");
  };
  const signOut = async () => { await supabase.auth.signOut(); setPage("Dashboard"); };

  const createTender = async () => {
    if (!title.trim()) return setMessage("Enter a tender title.");
    try {
      const tender = await api<Tender>("/tenders", {method:"POST", body:JSON.stringify({title, organization:organization || null})});
      if (file) { const form=new FormData(); form.append("file", file); await api("/tenders/"+tender.id+"/documents/upload",{method:"POST",body:form}); }
      setTitle(""); setOrganization(""); setFile(null); setMessage("Tender created successfully."); await loadTenders(); setPage("Tenders");
    } catch(e) { setMessage(e instanceof Error ? e.message : "Unable to create tender."); }
  };

  if (!session) return <div className="auth-page"><section className="auth-card"><h1>TenderIQ</h1><p className="muted">Tender intelligence for smarter bidding.</p><input type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)}/><input type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)}/><button className="primary full" onClick={signIn}>Sign in</button><button className="secondary full" onClick={signUp}>Create account</button>{message&&<p>{message}</p>}<small>Configure VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in the frontend environment.</small></section></div>;

  const checkApi = async () => { try { const r=await fetch(API_BASE+"/health"); setHealth(r.ok?"API online":"API error"); } catch { setHealth("API unreachable"); } };
  return <div className="app"><aside><h1>TenderIQ</h1><p className="muted">Tender Intelligence Platform</p>{["Dashboard","Tenders","Contractor Profile","Matches"].map(x=><button className={page===x?"nav active":"nav"} onClick={()=>setPage(x)} key={x}>{x}</button>)}<div className="side-bottom"><button onClick={checkApi}>Check API</button><span>{health}</span><button onClick={signOut}>Sign out</button></div></aside><main><header><div><p className="eyebrow">Tender Intelligence</p><h2>{page}</h2></div><button className="primary" onClick={()=>setPage("New Tender")}>+ New Tender</button></header>{page==="Dashboard"&&<Dashboard tenders={tenders}/>} {page==="Tenders"&&<TenderList tenders={tenders} onNew={()=>setPage("New Tender")}/>} {page==="New Tender"&&<section className="card form"><h3>Create tender</h3><input placeholder="Tender title *" value={title} onChange={e=>setTitle(e.target.value)}/><input placeholder="Organization" value={organization} onChange={e=>setOrganization(e.target.value)}/><label>Upload tender PDF<input type="file" accept="application/pdf" onChange={e=>setFile(e.target.files?.[0]||null)}/></label><button className="primary" onClick={createTender}>Create & Upload</button>{message&&<p>{message}</p>}</section>} {page==="Contractor Profile"&&<section className="card"><h3>Contractor Profile</h3><p className="muted">Company license, financial capacity, experience and equipment will be managed here.</p></section>} {page==="Matches"&&<section className="card"><h3>Tender Matches</h3><p className="muted">Requirement-by-requirement matching will appear here.</p></section>}</main></div>
}
function Dashboard({tenders}:{tenders:Tender[]}){return <><div className="hero"><div><h3>Know your tenders before you bid.</h3><p>Upload tender documents, extract requirements with AI, and compare them with your contractor profile.</p></div><button className="primary">Upload Tender PDF</button></div><div className="grid">{[[""+tenders.filter(t=>t.status==="new").length,"New Tenders"],[""+tenders.filter(t=>t.status==="processing").length,"Processing"],[""+tenders.filter(t=>t.status==="analyzed").length,"Analyzed"],["0","Potential Matches"]].map(([n,l])=><div className="stat card" key={l}><strong>{n}</strong><span>{l}</span></div>)}</div><section className="card"><h3>Recent tenders</h3>{tenders.length?<TenderList tenders={tenders.slice(0,5)}/>:<p className="muted">No tenders yet. Create your first tender.</p>}</section></>}
function TenderList({tenders,onNew}:{tenders:Tender[],onNew?:()=>void}){return <section className="card"><div className="row"><h3>Tenders</h3>{onNew&&<button className="primary" onClick={onNew}>+ New</button>}</div>{tenders.length?<div className="tender-list">{tenders.map(t=><div className="tender" key={t.id}><div><strong>{t.title}</strong><span>{t.organization||"Organization not specified"}</span></div><b>{t.status}</b></div>)}</div>:<p className="muted">No tenders found.</p>}</section>}
