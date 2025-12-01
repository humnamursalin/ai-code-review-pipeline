describe('Flask App E2E Tests', () => {
  it('should load the home page successfully', () => {
    cy.visit('/')
    cy.contains('AI Code Review Pipeline').should('be.visible')
    cy.contains('This app deploys automatically!').should('be.visible')
  })

  it('should return 200 status code', () => {
    cy.request({
      url: '/',
      failOnStatusCode: false
    }).then((response) => {
      expect(response.status).to.eq(200)
    })
  })

  it('should have proper HTML structure', () => {
    cy.visit('/')
    cy.get('h1').should('exist')
    cy.get('p').should('exist')
  })

  it('should be accessible and responsive', () => {
    cy.visit('/')
    cy.get('body').should('be.visible')
  })
})

