function alineDisplayRelation() {
	// Get the display-textbox (div) and display-relation (svg) elements
	const textDiv = document.getElementById("display-textbox");
	const svgContainer = document.getElementById("display-relation");
	// Get dimensions of the display-textbox
	const textDivRect = textDiv.getBoundingClientRect();
	// Set dimensions of the SVG container
	svgContainer.setAttribute("width", textDivRect.width);
	svgContainer.setAttribute("height", textDivRect.height);
}

function updateEntities() {
	// get input-text
    var text_ele = document.getElementById("text-input");
    var text = text_ele.value;
	// clear current display textbox
	var textElement = document.getElementById("display-textbox");
    textElement.innerHTML = '';
	// get entity elements
	var entityElement = document.getElementById("entity-store");
	var dataText = entityElement.getAttribute('data-json');
	// if no entities
	if (dataText === "") {
        var nonEntityElement = document.createElement("span");
        nonEntityElement.textContent = text;
        textElement.appendChild(nonEntityElement);
        return null;
      }
	
	entities = JSON.parse(dataText);
    entities.forEach(ent => {
      ent.start = parseInt(ent.start);
      ent.end = parseInt(ent.end);
    })
    entities.sort((a, b) => a.start - b.start);

    var i = 0;
    entities.forEach(ent => {
      // Non-entity text
      var nonEntityElement = document.createElement("span");
      nonEntityElement.textContent = text.substring(i, ent.start);
      textElement.appendChild(nonEntityElement);
      // Entity mark
      var entityElement = document.createElement("mark");
      entityElement.id = ent.entity_id;
      entityElement.className = "entity-mark";
      entityElement.textContent = text.substring(ent.start, ent.end);
      entityElement.style.backgroundColor = ent['color'];
      var entityTypeElement = document.createElement("span");
      entityTypeElement.className = "entity-type-tag";
      entityTypeElement.textContent = ent.entity_type
      entityElement.appendChild(entityTypeElement)
      textElement.appendChild(entityElement);
      i = ent.end;
    })
    // append text after last entity
    var nonEntityElement = document.createElement("span");
    lastEntity = entities[entities.length - 1]
    nonEntityElement.textContent = text.substring(lastEntity.end);
    textElement.appendChild(nonEntityElement);
  }

function updateRelations() {
	// Get the display-textbox (div) and display-relation (svg) elements
	const textDiv = document.getElementById("display-textbox");
	const svgContainer = document.getElementById("display-relation");
	const textDivRect = textDiv.getBoundingClientRect();
	// Clear current relation lines
	svgContainer.innerHTML = '';
	// iterate through relations
	const relationElement = document.getElementById("relation-store");
	const relations = JSON.parse(relationElement.getAttribute('data-json'));
	relations.forEach(rel => {
		const entity1Element = document.getElementById(rel.entity_1_id);
		const entity2Element = document.getElementById(rel.entity_2_id);
		const entity1Rect = entity1Element.getBoundingClientRect();
		const entity2Rect = entity2Element.getBoundingClientRect();

		// Handle line-broken entity
		// When an entity is split by line change, we use the top-left as StartX
		const entity1X = entity1Element.textContent.includes("\n")? entity1Rect.right - textDivRect.left : entity1Rect.left + entity1Rect.width / 2 - textDivRect.left;
		const entity1Y = entity1Rect.top - textDivRect.top;
		const entity2X = entity2Element.textContent.includes("\n")? entity2Rect.left - textDivRect.left : entity2Rect.left + entity2Rect.width / 2 - textDivRect.left;
		const entity2Y = entity2Rect.top - textDivRect.top;

		// start with entity on left
		var startX = null;
		var startY = null;
		var endX = null;
		var endY = null;
		if (entity1X < entity2X) {
			startX = entity1X;
			startY = entity1Y;
			endX = entity2X;
			endY = entity2Y;
		}
		else {
			startX = entity2X;
			startY = entity2Y;
			endX = entity1X;
			endY = entity1Y;
		}
		
		// Create the SVG path
		const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
		//path.className = "relation-path";
		// If start and end entities are on the same line
		if (startY === endY){
		path.setAttribute("d", `M${startX} ${startY} a 10 10 0 0 1 10 -10 L${endX - 10} ${startY - 10} a 10 10 0 0 1 10 10 L${endX} ${endY}`);
		}
		// If start entity is below end entities
		else if (startY > endY) {
		path.setAttribute("d", `M${startX} ${startY} L${startX} ${endY} a 10 10 0 0 1 10 -10 L${endX - 10} ${endY - 10} a 10 10 0 0 1 10 10 L${endX} ${endY}`);
		}
		// If start entity is above end entities
		else {
		path.setAttribute("d", `M${startX} ${startY} a 10 10 0 0 1 10 -10 L${endX - 10} ${startY - 10} a 10 10 0 0 1 10 10 L${endX} ${endY}`);  
		}
		path.setAttribute("class", "relation-path");
		svgContainer.appendChild(path);
		})
}


// This function wait until an element is rendered
const checkElement = async selector => {
    while ( document.getElementById(selector) === null) {
        await new Promise( resolve =>  requestAnimationFrame(resolve) )
    }
    return document.getElementById(selector);
};

// Place event-listener for display-textbox scroll 
checkElement("display-textbox").then((selector) => {
	selector.addEventListener('scroll', updateRelations);
})

checkElement("entity-store").then((element) => {
    // Create a new instance of MutationObserver
    const observer = new MutationObserver((mutationsList, observer) => {
        for (const mutation of mutationsList) {
            if (mutation.attributeName === 'data-json') {
                // Call your functions here
                alineDisplayRelation();
                updateEntities();
                updateRelations();
            }
        }
    });

    // Configuration of the observer
    const config = {
        attributes: true // Track changes to attributes
    };

    // Start observing the target node for configured mutations
    observer.observe(element, config);
});

checkElement("relation-store").then((element) => {
    // Create a new instance of MutationObserver
    const observer = new MutationObserver((mutationsList, observer) => {
        for (const mutation of mutationsList) {
            if (mutation.attributeName === 'data-json') {
                // Call your functions here
                alineDisplayRelation();
                updateEntities();
                updateRelations();
            }
        }
    });

    // Configuration of the observer
    const config = {
        attributes: true // Track changes to attributes
    };

    // Start observing the target node for configured mutations
    observer.observe(element, config);
});