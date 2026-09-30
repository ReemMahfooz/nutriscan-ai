let selectedConditions = new Set();

let currentUser = null;


/* =========================================================
   AUTHENTICATION
   ========================================================= */

function getToken() {
  return localStorage.getItem('nutriscan_token');
}


function setToken(token) {
  localStorage.setItem('nutriscan_token', token);
}


function clearToken() {
  localStorage.removeItem('nutriscan_token');
}


function authHeaders(includeJson = false) {

  const headers = {};

  const token = getToken();

  if (includeJson) {
    headers['Content-Type'] = 'application/json';
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
}


/* =========================================================
   REGISTER
   ========================================================= */

async function registerUser(event) {

  event.preventDefault();

  const name =
    document.getElementById('registerName').value.trim();

  const email =
    document.getElementById('registerEmail').value.trim();

  const password =
    document.getElementById('registerPassword').value;

  const message =
    document.getElementById('registerMessage');

  message.textContent = 'Creating account...';
  message.className = 'auth-message';


  try {

    const response = await fetch(
      '/api/auth/register',
      {
        method: 'POST',

        headers: {
          'Content-Type': 'application/json'
        },

        body: JSON.stringify({
          name,
          email,
          password
        })
      }
    );


    const data = await response.json();


    if (!response.ok) {

      throw new Error(
        data.detail || 'Registration failed.'
      );

    }


    message.textContent =
      'Registration successful. You can now log in.';

    message.className =
      'auth-message success';


    document.getElementById('registerForm').reset();


    document.getElementById('loginEmail').value =
      email;

  }

  catch (error) {

    message.textContent =
      error.message;

    message.className =
      'auth-message error';

  }

}


/* =========================================================
   LOGIN
   ========================================================= */

async function loginUser(event) {

  event.preventDefault();


  const email =
    document.getElementById('loginEmail').value.trim();

  const password =
    document.getElementById('loginPassword').value;


  const message =
    document.getElementById('loginMessage');


  message.textContent =
    'Logging in...';

  message.className =
    'auth-message';


  try {

    const response = await fetch(
      '/api/auth/login',
      {
        method: 'POST',

        headers: {
          'Content-Type': 'application/json'
        },

        body: JSON.stringify({
          email,
          password
        })
      }
    );


    const data = await response.json();


    if (!response.ok) {

      throw new Error(
        data.detail || 'Login failed.'
      );

    }


    /*
      The backend returns the JWT here.
    */

    setToken(data.access_token);


    message.textContent =
      'Login successful.';

    message.className =
      'auth-message success';


    /*
      Load the logged-in user's information.
    */

    await loadCurrentUser();


    /*
      Switch from login/register
      to the main application.
    */

    document
      .getElementById('authSection')
      .classList.add('hidden');


    document
      .getElementById('appSection')
      .classList.remove('hidden');


    /*
      Load personalized information.
    */

    await loadConditions();

    await loadMyConditions();

    await loadHistory();

  }

  catch (error) {

    clearToken();

    message.textContent =
      error.message;

    message.className =
      'auth-message error';

  }

}


/* =========================================================
   LOAD CURRENT USER
   ========================================================= */

async function loadCurrentUser() {

  const response = await fetch(
    '/api/auth/me',
    {
      headers: authHeaders()
    }
  );


  const data = await response.json();


  if (!response.ok) {

    clearToken();

    throw new Error(
      data.detail || 'Authentication failed.'
    );

  }


  currentUser = data;


  document.getElementById('userName').textContent =
    data.name;

  document.getElementById('userEmail').textContent =
    data.email;

}


/* =========================================================
   LOGOUT
   ========================================================= */

function logout() {

  clearToken();

  currentUser = null;

  selectedConditions.clear();


  document
    .getElementById('appSection')
    .classList.add('hidden');


  document
    .getElementById('authSection')
    .classList.remove('hidden');


  document.getElementById('loginMessage').textContent =
    'You have been logged out.';

  document.getElementById('loginMessage').className =
    'auth-message success';

}


/* =========================================================
   LOAD AVAILABLE HEALTH CONDITIONS
   ========================================================= */

async function loadConditions() {

  const box =
    document.getElementById('conditions');


  try {

    const response = await fetch(
      '/api/conditions'
    );


    if (!response.ok) {

      throw new Error(
        'Could not load health conditions.'
      );

    }


    const conditions =
      await response.json();


    box.innerHTML = '';


    if (!conditions.length) {

      box.innerHTML =
        '<p>No health conditions are available.</p>';

      return;

    }


    conditions.forEach(condition => {

      const button =
        document.createElement('button');


      button.type =
        'button';


      button.className =
        'condition';


      button.textContent =
        condition.name;


      button.dataset.conditionId =
        condition.id;


      button.onclick = () => {

        if (
          selectedConditions.has(
            condition.id
          )
        ) {

          selectedConditions.delete(
            condition.id
          );

          button.classList.remove(
            'selected'
          );

        }

        else {

          selectedConditions.add(
            condition.id
          );

          button.classList.add(
            'selected'
          );

        }

      };


      box.appendChild(button);

    });

  }

  catch (error) {

    box.innerHTML =
      `<p class="error">${escapeHtml(error.message)}</p>`;

  }

}


/* =========================================================
   LOAD USER'S SAVED CONDITIONS
   ========================================================= */

async function loadMyConditions() {

  try {

    const response = await fetch(
      '/api/health/conditions',
      {
        headers: authHeaders()
      }
    );


    const data =
      await response.json();


    if (!response.ok) {

      throw new Error(
        data.detail ||
        'Could not load your health conditions.'
      );

    }


    selectedConditions =
      new Set(data.conditions || []);


    /*
      Visually select the buttons
      corresponding to the user's conditions.
    */

    document
      .querySelectorAll('.condition')
      .forEach(button => {

        const conditionId =
          button.dataset.conditionId;


        if (
          selectedConditions.has(
            conditionId
          )
        ) {

          button.classList.add(
            'selected'
          );

        }

        else {

          button.classList.remove(
            'selected'
          );

        }

      });

  }

  catch (error) {

    console.error(
      'Could not load saved conditions:',
      error
    );

  }

}


/* =========================================================
   SAVE USER'S CONDITIONS
   ========================================================= */

async function saveConditions() {

  const message =
    document.getElementById(
      'conditionMessage'
    );


  const conditionIds =
    Array.from(selectedConditions);


  try {

    const response = await fetch(
      '/api/health/conditions',
      {
        method: 'PUT',

        headers: authHeaders(true),

        body: JSON.stringify({
          condition_ids: conditionIds
        })
      }
    );


    const data =
      await response.json();


    if (!response.ok) {

      throw new Error(
        data.detail ||
        'Could not save health conditions.'
      );

    }


    message.textContent =
      'Health conditions saved successfully.';

    message.className =
      'condition-save-message success';

  }

  catch (error) {

    message.textContent =
      error.message;

    message.className =
      'condition-save-message error';

  }

}


/* =========================================================
   ANALYZE FOOD
   ========================================================= */

async function analyze() {

  const text =
    document
      .getElementById('ingredients')
      .value
      .trim();


  if (!text) {

    alert(
      'Please enter ingredients.'
    );

    return;

  }


  if (!getToken()) {

    alert(
      'Please log in first.'
    );

    return;

  }


  const button =
    document.getElementById(
      'analyzeBtn'
    );


  button.disabled =
    true;


  button.textContent =
    'Analyzing...';


  try {

    const ingredients =
      text
        .split(',')
        .map(
          ingredient =>
            ingredient.trim()
        )
        .filter(Boolean);


    const response =
      await fetch(
        '/api/analyze',
        {
          method: 'POST',

          headers:
            authHeaders(true),

          body: JSON.stringify({
            conditions:
              Array.from(
                selectedConditions
              ),

            ingredients:
              ingredients
          })
        }
      );


    const data =
      await response.json();


    if (!response.ok) {

      throw new Error(
        data.detail ||
        'Analysis failed.'
      );

    }


    showResult(data);


    /*
      Refresh the user's history
      after saving the analysis.
    */

    await loadHistory();

  }

  catch (error) {

    alert(
      error.message
    );

  }

  finally {

    button.disabled =
      false;

    button.textContent =
      'Analyze Safety Risks';

  }

}


/* =========================================================
   DISPLAY ANALYSIS RESULT
   ========================================================= */

function showResult(data) {

  const box =
    document.getElementById(
      'result'
    );


  box.classList.remove(
    'hidden'
  );


  let html = `

    <h2>
      4. Analysis Result
    </h2>

    <div class="score">
      ${escapeHtml(data.safety_score)}/100
    </div>

    <h3>
      ${escapeHtml(data.status)}
    </h3>

  `;


  /*
    Flagged ingredients
  */

  if (
    data.flagged_ingredients &&
    data.flagged_ingredients.length
  ) {

    html +=
      '<h3>Flagged Ingredients</h3>';


    data.flagged_ingredients
      .forEach(item => {

        html += `

          <div class="alert">

            <b>
              ${escapeHtml(item.ingredient)}
            </b>

            →
            ${escapeHtml(item.condition_triggered)}

            <br>

            ${escapeHtml(item.warning)}

          </div>

        `;

      });

  }

  else {

    html += `

      <div class="safe">

        No matching high-risk ingredients
        were found for the selected conditions.

      </div>

    `;

  }


  /*
    Suggested substitutions
  */

  if (
    data.suggested_substitutions
  ) {

    const substitutions =
      Object.entries(
        data.suggested_substitutions
      );


    if (substitutions.length) {

      html +=
        '<h3>Suggested Substitutions</h3>';


      html += '<ul>';


      substitutions.forEach(
        ([from, to]) => {

          html += `

            <li>

              <b>
                ${escapeHtml(from)}
              </b>

              →

              ${escapeHtml(to)}

            </li>

          `;

        }
      );


      html += '</ul>';

    }

  }


  box.innerHTML =
    html;


  box.scrollIntoView({
    behavior: 'smooth',
    block: 'start'
  });

}


/* =========================================================
   OPEN FOOD FACTS PRODUCT LOOKUP
   ========================================================= */

async function lookupProduct() {

  const barcodeInput =
    document.getElementById(
      'barcode'
    );


  const productInfo =
    document.getElementById(
      'productInfo'
    );


  const ingredientsBox =
    document.getElementById(
      'ingredients'
    );


  const barcode =
    barcodeInput.value.trim();


  if (!barcode) {

    alert(
      'Please enter a product barcode.'
    );

    return;

  }


  productInfo.classList.remove(
    'hidden'
  );


  productInfo.innerHTML =
    'Looking up product...';


  try {

    const response =
      await fetch(
        `/api/product/${encodeURIComponent(barcode)}`
      );


    const data =
      await response.json();


    if (!response.ok) {

      throw new Error(
        data.detail ||
        'Product could not be found.'
      );

    }


    productInfo.innerHTML = `

      <h3>
        ${escapeHtml(
          data.product_name ||
          'Product found'
        )}
      </h3>

      <p>

        <b>Brand:</b>

        ${escapeHtml(
          data.brands ||
          'Not available'
        )}

      </p>

    `;


    if (data.ingredients) {

      /*
        Open Food Facts returned
        ingredient information.
      */

      ingredientsBox.value =
        data.ingredients;

    }

    else {

      /*
        No ingredients were returned.
        User can type them manually.
      */

      ingredientsBox.value = '';


      productInfo.innerHTML += `

        <p>

          <b>
            Ingredients were not available
            for this product.
          </b>

          Please enter them manually.

        </p>

      `;

    }

  }

  catch (error) {

    productInfo.innerHTML = `

      <p class="error">

        ${escapeHtml(
          error.message
        )}

      </p>

    `;

  }

}


/* =========================================================
   LOAD USER HISTORY
   ========================================================= */

async function loadHistory() {

  const box =
    document.getElementById(
      'history'
    );


  if (!getToken()) {

    box.textContent =
      'Please log in to view your history.';

    return;

  }


  try {

    const response =
      await fetch(
        '/api/history',
        {
          headers:
            authHeaders()
        }
      );


    const rows =
      await response.json();


    if (!response.ok) {

      throw new Error(
        rows.detail ||
        'Could not load history.'
      );

    }


    if (!rows.length) {

      box.textContent =
        'No analyses saved yet.';

      return;

    }


    box.innerHTML =
      rows
        .map(row => `

          <div class="history-row">

            <b>

              ${escapeHtml(
                row.status
              )}

              —

              ${escapeHtml(
                row.safety_score
              )}/100

            </b>

            <br>

            <small>

              Conditions:

              ${escapeHtml(
                (row.conditions || [])
                  .join(', ') ||
                'None'
              )}

              <br>

              ${new Date(
                row.created_at
              ).toLocaleString()}

            </small>

          </div>

        `)
        .join('');

  }

  catch (error) {

    box.innerHTML =
      `<p class="error">${escapeHtml(error.message)}</p>`;

  }

}


/* =========================================================
   HTML ESCAPING
   ========================================================= */

function escapeHtml(value) {

  return String(value)

    .replaceAll(
      '&',
      '&amp;'
    )

    .replaceAll(
      '<',
      '&lt;'
    )

    .replaceAll(
      '>',
      '&gt;'
    )

    .replaceAll(
      '"',
      '&quot;'
    )

    .replaceAll(
      "'",
      '&#039;'
    );

}


/* =========================================================
   INITIALIZE APPLICATION
   ========================================================= */

async function initializeApp() {

  /*
    Connect the forms.
  */

  document
    .getElementById('registerForm')
    .addEventListener(
      'submit',
      registerUser
    );


  document
    .getElementById('loginForm')
    .addEventListener(
      'submit',
      loginUser
    );


  /*
    If there is no JWT,
    show the login/register screen.
  */

  if (!getToken()) {

    return;

  }


  /*
    If a JWT exists, try to restore
    the previous login session.
  */

  try {

    await loadCurrentUser();


    document
      .getElementById('authSection')
      .classList.add('hidden');


    document
      .getElementById('appSection')
      .classList.remove('hidden');


    await loadConditions();

    await loadMyConditions();

    await loadHistory();

  }

  catch (error) {

    /*
      Token is invalid or expired.
      Return to login screen.
    */

    clearToken();

    document
      .getElementById('authSection')
      .classList.remove('hidden');


    document
      .getElementById('appSection')
      .classList.add('hidden');

  }

}


/* =========================================================
   START
   ========================================================= */

initializeApp();