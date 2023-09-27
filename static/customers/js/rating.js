const form1 = document.getElementById("my-form-1");
const outputDisplay1 = document.getElementById("form-data-display-1");

const form2 = document.getElementById("my-form-2");
const outputDisplay2 = document.getElementById("form-data-display-2");

const noDataWarning = "No data selected";

const onSubmit = ({ formElem, displayElem }) => (event) => {
  event.preventDefault();
  const data = Array.from(new FormData(formElem));
  const serializedData = data
    .map(([fieldName, value]) => `${fieldName} = ${value}`)
    .join("\n");
  displayElem.insertAdjacentText(
    "beforeend",
    !!data.length ? serializedData + "\n" : noDataWarning + "\n"
  );
};

form1.addEventListener(
  "submit",
  onSubmit({ formElem: form1, displayElem: outputDisplay1 })
);

form2.addEventListener(
  "submit",
  onSubmit({ formElem: form2, displayElem: outputDisplay2 })
);
