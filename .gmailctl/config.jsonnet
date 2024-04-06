// Uncomment if you want to use the standard library.
// local lib = import 'gmailctl.libsonnet';
{
  version: "v1alpha3",
  author: {
    name: "Harry H",
    email: "h@stmharry.io",
  },
  // Note: labels management is optional. If you prefer to use the
  // GMail interface to add and remove labels, you can safely remove
  // this section of the config.
  labels: [
    // Labels - Orgs
    {
      name: "Hashgreen",
      color: {
        background: "#006633",
        text: "#f1f5ec",
      },
    },
    {
      name: "CodeGreen",
      color: {
        background: "#ff7537",
        text: "#ffffff",
      },
    },
    {
      name: "OpenCGT",
      color: {
        background: "#fb4c2f",
        text: "#ffffff",
      },
    },
    {
      name: "Green Card",
      color: {
        background: "#42d692",
        text: "#094228",
      },
    },
    { name: "Statement" },
    { name: "Crypto" },
    { name: "Calendar" },
  ],
  rules: [
    // Organization

    {
      filter: {
        to: "@hashgreen.net",
      },
      actions: {
        labels: [ "Hashgreen" ],
      },
    },

    {
      filter: {
        to: "@codegreen.org",
      },
      actions: {
        labels: [ "CodeGreen" ],
      },
    },

    {
      filter: {
        to: "@opencgt.com",
      },
      actions: {
        labels: [ "OpenCGT" ],
      },
    },

    // Important Topics

    {
      filter: {
        subject: "Green Card",
        isEscaped: true,
      },
      actions: {
        markSpam: false,
        markImportant: true,
        labels: [ "Green Card" ],
      },
    },

    {
      filter: {
        or: [
          { from: "donotreplyAPAC@mail.rci.com" },
          { from: "club365@mail.welcometoyourclub.com" },
          { from: "info@email.atlantisbahamas.com" },
        ],
      },
      actions: {
        forward: "chelsea850416@gmail.com",
      },
    },

    // Actions Needed

    {
      filter: {
        or: [
          // Sinopac Bank
          { from: "ebillservice@newebill.banksinopac.com.tw" },
          // TaiShin Bank
          { from: "webmaster@bhurecv.taishinbank.com.tw" },
          // CTBC Bank
          { from: "ebill@estats.ctbcbank.com" },
          // E-Sun Bank
          { from: "estatement@esunbank.com" },
        ],
      },
      actions: {
        markSpam: false,
        markImportant: true,
        labels: [ "Statement" ],
      },
    },

    // Attention Needed

    {
      filter: {
        or: [
          { from: "no_reply@swingvy.com" },
          { from: "support@github.com" },
        ],
      },
      actions: {
        markSpam: false,
        markImportant: true,
      },
    },

    {
      filter: {
        or: [
          { from: "no-reply@info.coinbase.com" },
          { from: "noreply@mailer1.okx.com" },
          { from: "noreply@mailer2.okx.com" },
          { from: "support@ace.io" },
        ],
      },
      actions: {
        markSpam: false,
        labels: [ "Crypto" ],
      },
    },

    // Unimportant But Needs To Be Archived

    {
      filter: {
        has: "invite.ics",
      },
      actions: {
        markSpam: false,
        markImportant: false,
        archive: true,
        labels: [ "Calendar" ],
        category: "updates",
      },
    },

    {
      filter: {
        or: [
          // Google
          { from: "payments-noreply@google.com" },
          // GoShare
          { from: "no-reply@ridegoshare.com" },
          // WeMo Scooter
          { from: "receipt@wemoscooter.com" },
          { from: "invoice@mail.ei.com.tw" },
          // PX Mart
          { from: "pxmart@l.tradevan.com.tw" },
          // Shopee
          { from: "b2ceci@ecimail1.tradevan.com.tw" },
          // ChungHwa Telecom
          { from: "service@idealcard.com.tw" },
          // Uber
          { from: "noreply@uber.com" },
          { from: "noreply@uberegui.com" },
          // TW Mobile
          { from: "ebill@ebsmtp01.taiwanmobile.com" },

          // Sinopac Bank
          { from: "paybill@sinopac.com" },
          { from: "mma@sinopac.com" },
          { from: "SpendService@sinopac.com" },
          { from: "NotifyService@sinopac.com" },
          { from: "donotreply.sec@sinopac.com" },
          // TaiShin Bank
          { from: "richart@richart.tw" },
          { from: "webmaster@taishinbank.com.tw" },
          { from: "TSB@mhurcv.taishinbank.com.tw" },
          // CTBC Bank
          { from: "bank.csc@inib.ctbcbank.com" },
          { from: "bank.csc@inedm.ctbcbank.com" },
          // Fubon Bank
          { from: "mbank@dfm.taipeifubon.com.tw" },
          { from: "ebank@dfm.taipeifubon.com.tw" },
          { from: "service@mhu.taipeifubon.com.tw" },
          // E-Sun Bank
          { from: "NetbankService@esunbank.com" },
          { from: "ESUNCARD@email.esunbank.com.tw" },
          { from: "Service@info.esunbank.com" },
          { from: "Service@msg.esunbank.com" },
          { from: "esunb2b@gibbhrcv.esunbank.com" },
          // DBS Bank
          { from: "no-reply@msg.dbs.com" },

          // Discover
          { from: "discover@card-e.em.discover.com" },

          // Misc
          { from: "account-update@amazon.com" },
          { from: "numerai@numer.ai" },
          { from: "notifications@github.com" },
          { from: "noreply@github.com" },
          { from: "jira@codegreenlabs.atlassian.net" },
          { replyto: "cloud-support@confluent.io" },
          { from: "comments-noreply@docs.google.com" },
        ],
      },
      actions: {
        archive: true,
        category: "updates",
      },
    },

    // Spam

    {
      filter: {
        or: [
          { from: "newsletter@gbbcouncil.org" },
          { from: "support@s.usa.experian.com" },
          { from: "notifications@mvgx.com" },
          { list: "catchall@codegreen.org" },
          { to: "jason@codegreen.org" },
        ],
      },
      actions: {
        delete: true,
      },
    },
  ],
}
