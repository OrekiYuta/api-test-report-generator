//  Jaeger Get SQL Statement in Chrome Console

//  example: open the url https://
//  press key F12 open the chrome console


//  1.open the jpaDataSource Node to load full element
const elements = Array.from(document.querySelectorAll('*'));

elements.forEach(element => {
    if (element.textContent.includes('jpaDataSource')) {
        element.click();
    }
});



//  2.get SQL Statement in jdbc.query Node
const elementsWithClass = document.querySelectorAll('li.AccordianKeyValues--summaryItem');

const uniqueTextContents = new Set();

elementsWithClass.forEach(element => {
    const textContent = element.textContent.trim();
    if (textContent.includes('jdbc.query=')) {
        uniqueTextContents.add(textContent.replace('jdbc.query=', ''));
    }
});

const formattedTextContent = [...uniqueTextContents].join('\n\n');

console.log(formattedTextContent);

//  3.copy and paste the chrome console output content to the master data excel