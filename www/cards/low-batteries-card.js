import {
  LitElement,
  html,
  css
} from "https://unpkg.com/lit-element@2.0.1/lit-element.js?module";

class LowBatteriesCard extends LitElement {
    
  static get properties() {
    return {
      hass: {},
      config: {}
    };
  }

  render() {
    return html`
        <ha-card>
            ${this.config.entities.map((entity) => {
            console.log(this.hass);
                const state = this.hass.states[entity]
                
               console.log('state', state); 
            })}
        </ha-card>
    `;
  }

  setConfig(config) {
    if (!config.entities) {
      throw new Error("You need to define entities");
    }
    this.config = config;
  }

  getCardSize() {
    return this.config.entities.length + 1;
  }



  static get styles() {
    return css`
    `;
  }
}

customElements.define("low-batteries-card", LowBatteriesCard);
