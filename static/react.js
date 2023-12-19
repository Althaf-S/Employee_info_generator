'use strict';

function Like(){
  
   console.log("Hello world!!!");
   
   const [text, setText] = React.useText('')
   const [state, setState] = React.useState([])
   
   
   return (<div>
           <input type="text" value={state} onChange={(e) => setState(e.target.value)}/>
           </div>)
   
}


const domContainer = document.getElementById('root');
const root = ReactDOM.createRoot(domContainer);
root.render(React.createElement(Like));
