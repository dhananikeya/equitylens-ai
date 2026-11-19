export default function({parentElement,data,setTriggerValue}) {
  const root=parentElement.querySelector(".el-action-grid");
  if(!root) return;
  root.replaceChildren();
  for(const [i,item] of (data?.actions ?? []).entries()){
    const button=document.createElement("button");
    button.type="button";
    button.className="el-action";
    const top=document.createElement("span"); top.className="el-action-top";
    const num=document.createElement("span"); num.className="el-action-number"; num.textContent=String(i+1).padStart(2,"0")+" / EXPLORE";
    const arrow=document.createElement("span"); arrow.className="el-action-arrow"; arrow.setAttribute("aria-hidden","true"); arrow.textContent="↗";
    top.append(num,arrow);
    const title=document.createElement("span"); title.className="el-action-title"; title.textContent=item.label;
    const detail=document.createElement("span"); detail.className="el-action-description"; detail.textContent=item.description;
    button.append(top,title,detail);
    button.addEventListener("click",()=>setTriggerValue("destination",item.destination));
    root.append(button);
  }
}